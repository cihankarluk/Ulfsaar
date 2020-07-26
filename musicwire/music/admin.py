from django.contrib import admin

from musicwire.music.models import PlaylistTrack, Playlist

admin.site.register(PlaylistTrack)
admin.site.register(Playlist)
