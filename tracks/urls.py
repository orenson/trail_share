from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('explore/', views.explore_view, name='explore'),
    path('groups/create/', views.create_group_view, name='create_group'),
    path('groups/<slug:slug>/', views.group_detail_view, name='group_detail'),
    path('groups/<slug:slug>/join/', views.join_group_view, name='join_group'),
    path('groups/<slug:slug>/leave/', views.leave_group_view, name='leave_group'),
    path('groups/<slug:slug>/upload/', views.upload_track_view, name='upload_track'),
    path('groups/<slug:slug>/rotate-invite/', views.rotate_invite_view, name='rotate_invite'),
    path('invite/<uuid:token>/', views.invite_join_view, name='invite_join'),
    path('tracks/<int:pk>/', views.track_detail_view, name='track_detail'),
    path('tracks/<int:pk>/delete/', views.delete_track_view, name='delete_track'),
]
