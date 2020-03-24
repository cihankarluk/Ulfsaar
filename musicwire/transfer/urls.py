from django.urls import path

from musicwire.transfer import views

urlpatterns = [
    path('', views.TransferPlaylistsView.as_view(), name='transfer'),
]
