from django.urls import path

from musicwire.music import views

urlpatterns = [
    path('playlist/', views.PlaylistView.as_view(), name='playlist'),
    path('playlist/create/', views.CreatePlaylistView.as_view(), name='create_playlist'),
    path('track/', views.TrackView.as_view(), name='track')
]