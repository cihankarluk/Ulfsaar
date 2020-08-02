from django.db import models

from musicwire.account.models import UserProfile
from musicwire.provider.models import Provider


class Playlist(models.Model):
    PUBLIC = "public"
    PRIVATE = "private"

    STATUS = (
        (PUBLIC, "public"),
        (PRIVATE, "private")
    )

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=12, choices=STATUS)
    remote_id = models.CharField(max_length=64)
    content = models.CharField(max_length=64, null=True)
    provider = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    is_transferred = models.BooleanField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class PlaylistTrack(models.Model):
    name = models.CharField(max_length=256)
    artist = models.CharField(max_length=128, null=True)
    album = models.CharField(max_length=128, null=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True)
    remote_id = models.CharField(max_length=155)
    is_transferred = models.BooleanField(default=False)
    provider = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class SearchErrorTracks(models.Model):
    name = models.CharField(max_length=256)
    response = models.CharField(max_length=256)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
