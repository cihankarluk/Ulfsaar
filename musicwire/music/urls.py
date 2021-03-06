from django.urls import path

from musicwire.music import views

urlpatterns = [
    path('playlist/', views.PlaylistView.as_view(), name='playlist'),
    path('playlist/track/', views.PlaylistTrackView.as_view(), name='playlist_track'),
    path('playlist/create/', views.CreatePlaylistView.as_view(), name='create_playlist'),
    path('playlist/track/add/', views.AddTrackToPlaylistView.as_view(), name='add_track'),
    path('search/', views.SearchView.as_view(), name='search')
]