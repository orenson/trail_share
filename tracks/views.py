import json
import urllib.parse
import gpxpy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Group, Track
from .forms import GroupForm, TrackUploadForm


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    recent_groups = Group.objects.filter(is_private=False)[:6]
    return render(request, 'tracks/home.html', {'recent_groups': recent_groups})


@login_required
def dashboard_view(request):
    user = request.user
    my_groups = Group.objects.filter(
        Q(creator=user) | Q(members=user)
    ).distinct()
    recent_tracks = Track.objects.filter(
        group__in=my_groups
    ).select_related('uploaded_by', 'group')[:12]
    public_groups = Group.objects.filter(is_private=False).exclude(
        Q(creator=user) | Q(members=user)
    )[:6]
    return render(request, 'tracks/dashboard.html', {
        'my_groups': my_groups,
        'recent_tracks': recent_tracks,
        'public_groups': public_groups,
    })


@login_required
def create_group_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, f'Group "{group.name}" created!')
            return redirect('group_detail', slug=group.slug)
    else:
        form = GroupForm()
    return render(request, 'tracks/create_group.html', {'form': form})


@login_required
def group_detail_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    user = request.user
    is_member = user == group.creator or group.members.filter(pk=user.pk).exists()

    if group.is_private and not is_member:
        messages.error(request, 'This group is private. You need an invite link to join.')
        return redirect('dashboard')

    tracks = group.tracks.select_related('uploaded_by').all()
    invite_url = request.build_absolute_uri(f'/invite/{group.invite_token}/')

    return render(request, 'tracks/group_detail.html', {
        'group': group,
        'tracks': tracks,
        'is_member': is_member,
        'invite_url': invite_url,
    })


@login_required
def join_group_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if group.is_private:
        messages.error(request, 'This group is private. Use the invite link to join.')
        return redirect('explore')
    if not group.members.filter(pk=request.user.pk).exists():
        group.members.add(request.user)
        messages.success(request, f'Joined "{group.name}"!')
    return redirect('group_detail', slug=slug)


def invite_join_view(request, token):
    group = get_object_or_404(Group, invite_token=token)
    if not request.user.is_authenticated:
        messages.info(request, f'Sign in or register to join "{group.name}".')
        return redirect(f'/accounts/login/?next=/invite/{token}/')
    if request.user == group.creator or group.members.filter(pk=request.user.pk).exists():
        messages.info(request, f'You are already a member of "{group.name}".')
        return redirect('group_detail', slug=group.slug)
    group.members.add(request.user)
    messages.success(request, f'You have joined "{group.name}" via invite link!')
    return redirect('group_detail', slug=group.slug)


@login_required
def rotate_invite_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if request.user != group.creator:
        messages.error(request, 'Only the group creator can reset the invite link.')
        return redirect('group_detail', slug=slug)
    if request.method == 'POST':
        group.rotate_invite_token()
        messages.success(request, 'Invite link has been reset. The old link is now invalid.')
    return redirect('group_detail', slug=slug)


@login_required
def leave_group_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if request.user == group.creator:
        messages.error(request, "You can't leave a group you created.")
        return redirect('group_detail', slug=slug)
    group.members.remove(request.user)
    messages.info(request, f'You have left "{group.name}".')
    return redirect('dashboard')


@login_required
def upload_track_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    user = request.user
    is_member = user == group.creator or group.members.filter(pk=user.pk).exists()
    if not is_member:
        messages.error(request, 'You must be a member to upload tracks.')
        return redirect('group_detail', slug=slug)

    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.group = group
            track.uploaded_by = user
            track.save()
            track.parse_gpx_stats()
            track.save()
            messages.success(request, f'Track "{track.title}" uploaded!')
            return redirect('track_detail', pk=track.pk)
    else:
        form = TrackUploadForm()
    return render(request, 'tracks/upload_track.html', {'form': form, 'group': group})


@login_required
def track_detail_view(request, pk):
    track = get_object_or_404(Track, pk=pk)
    group = track.group
    user = request.user
    is_member = user == group.creator or group.members.filter(pk=user.pk).exists()

    if group.is_private and not is_member:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    # Build gpx.studio embed URL using the correct format
    file_url = request.build_absolute_uri(track.gpx_file.url)
    options = json.dumps({"files": [file_url], "basemap": "openStreetMap"})
    gpxstudio_url = f"https://gpx.studio/embed?options={urllib.parse.quote(options)}"

    return render(request, 'tracks/track_detail.html', {
        'track': track,
        'group': group,
        'is_member': is_member,
        'gpxstudio_url': gpxstudio_url,
    })


@login_required
def delete_track_view(request, pk):
    track = get_object_or_404(Track, pk=pk)
    if track.uploaded_by != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('track_detail', pk=pk)
    if request.method == 'POST':
        group_slug = track.group.slug
        track.gpx_file.delete(save=False)
        track.delete()
        messages.success(request, 'Track deleted.')
        return redirect('group_detail', slug=group_slug)
    return render(request, 'tracks/confirm_delete.html', {'track': track})


def explore_view(request):
    q = request.GET.get('q', '')
    groups = Group.objects.filter(is_private=False)
    if q:
        groups = groups.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, 'tracks/explore.html', {'groups': groups, 'q': q})
