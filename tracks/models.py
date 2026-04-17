from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
import gpxpy


def gpx_upload_path(instance, filename):
    return f'gpx/{instance.group.slug}/{uuid.uuid4().hex[:8]}_{filename}'


class Group(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='joined_groups', blank=True)
    is_private = models.BooleanField(default=False)
    cover_color = models.CharField(max_length=7, default='#2D6A4F')
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Group.objects.filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()

    def track_count(self):
        return self.tracks.count()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('group_detail', args=[self.slug])

    def rotate_invite_token(self):
        self.invite_token = uuid.uuid4()
        self.save(update_fields=['invite_token'])


class Track(models.Model):
    ACTIVITY_CHOICES = [
        ('hiking', 'Hiking'),
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('mtb', 'Mountain Biking'),
        ('skiing', 'Skiing'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    gpx_file = models.FileField(upload_to=gpx_upload_path)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='tracks')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='hiking')
    distance_km = models.FloatField(null=True, blank=True)
    elevation_gain_m = models.FloatField(null=True, blank=True)
    elevation_loss_m = models.FloatField(null=True, blank=True)
    max_elevation_m = models.FloatField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def parse_gpx_stats(self):
        try:
            with open(self.gpx_file.path, 'r') as f:
                gpx = gpxpy.parse(f)
            length = gpx.length_3d() or gpx.length_2d()
            self.distance_km = round(length / 1000, 2) if length else None
            uphill, downhill = gpx.get_uphill_downhill()
            self.elevation_gain_m = round(uphill, 1) if uphill else None
            self.elevation_loss_m = round(downhill, 1) if downhill else None
            elevations = [p.elevation for t in gpx.tracks for s in t.segments
                          for p in s.points if p.elevation is not None]
            if elevations:
                self.max_elevation_m = round(max(elevations), 1)
            duration = gpx.get_duration()
            self.duration_seconds = int(duration) if duration else None
        except Exception:
            pass

    def get_duration_display(self):
        if not self.duration_seconds:
            return None
        h = self.duration_seconds // 3600
        m = (self.duration_seconds % 3600) // 60
        return f'{h}h {m}m' if h else f'{m}m'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('track_detail', args=[self.pk])

    @property
    def activity_icon(self):
        return {'hiking': '🥾', 'running': '🏃', 'cycling': '🚴',
                'mtb': '🚵', 'skiing': '⛷️', 'other': '📍'}.get(self.activity_type, '📍')
