from django.contrib.postgres.fields import JSONField
from django.db import models

from musicwire.account.models import UserProfile
from musicwire.provider.models import Provider


class TransferError(models.Model):
    PLAYLIST = "playlist"
    TRACK = "track"

    TYPE = (
        (PLAYLIST, "playlist"),
        (TRACK, "track")
    )

    request_data = JSONField()
    error = models.TextField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    source = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    end = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    type = models.CharField(max_length=64, choices=TYPE)

    def __str__(self):
        return f"{self.source} -> {self.end}/{self.type}"
