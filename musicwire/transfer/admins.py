from django.contrib import admin

from musicwire.transfer.models import TransferredPlaylists, TransferredTracks

admin.site.register(TransferredPlaylists)
admin.site.register(TransferredTracks)
