from django.db import models

from musicwire.account.models import UserProfile
from musicwire.provider.models import Provider


class Playlist(models.Model):
    name = models.CharField(max_length=256)
    status = models.CharField(max_length=64)
    remote_id = models.CharField(max_length=64)
    content = models.CharField(max_length=64, null=True)
    provider = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    is_transferred = models.BooleanField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


class PlaylistTrack(models.Model):
    name = models.CharField(max_length=256)
    artist = models.CharField(max_length=128, null=True)
    album = models.CharField(max_length=128, null=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True)
    remote_id = models.CharField(max_length=155)
    is_transferred = models.BooleanField(default=False)
    provider = models.CharField(max_length=64, choices=Provider.PROVIDERS)
