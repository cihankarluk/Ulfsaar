from django.contrib import admin

from musicwire.music.models import PlaylistTrack, Playlist, SearchErrorTracks

admin.site.register(PlaylistTrack)
admin.site.register(Playlist)
admin.site.register(SearchErrorTracks)
