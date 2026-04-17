from django.contrib import admin
from .models import Group, Track

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'is_private', 'created_at']

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'group', 'activity_type', 'distance_km', 'created_at']
