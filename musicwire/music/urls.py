from django.urls import path

from musicwire.music import views

urlpatterns = [
    path('playlist/', views.PlaylistView.as_view(), name='playlist'),
    path('track/', views.TrackView.as_view(), name='track')
]