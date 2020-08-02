from django.db import models

from musicwire.music.models import Playlist
from musicwire.provider.models import Provider


class TransferredPlaylists(models.Model):
    SUCCESS = "success"
    FAILED = "failed"

    TRANSFER_STATUSES = (
        (SUCCESS, 'success'),
        (FAILED, 'failed')
    )

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=12, choices=Playlist.STATUS)
    remote_id = models.CharField(max_length=64)
    content = models.CharField(max_length=64, null=True)
    source = models.CharField(max_length=64, choices=Provider.PROVIDERS, null=True)
    end = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    transfer_status = models.CharField(max_length=12, choices=TRANSFER_STATUSES)


class TransferredTracks(models.Model):
    name = models.CharField(max_length=255)
    transferred_playlist = models.ForeignKey(TransferredPlaylists, on_delete=models.SET_NULL, null=True)
    remote_id = models.CharField(max_length=255)
    source = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    end = models.CharField(max_length=64, choices=Provider.PROVIDERS)
    transfer_status = models.CharField(max_length=12, choices=TransferredPlaylists.TRANSFER_STATUSES)
