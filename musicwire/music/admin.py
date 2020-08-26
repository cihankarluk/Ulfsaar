from django.contrib import admin

from musicwire.music.models import PlaylistTrack, Playlist, SearchErrorTrack, \
    CreatedPlaylist


class PlaylistModelAdmin(admin.ModelAdmin):
    list_display = 'name', 'status', 'provider', 'is_transferred', 'user'
    search_fields = 'name', 'provider', 'is_transferred', 'user__username'
    readonly_fields = 'name', 'status', 'provider', 'remote_id', 'user', 'content'


class PlaylistTrackModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'playlist',
                    'provider', 'is_transferred', 'user')
    search_fields = ('name', 'artist', 'album', 'playlist',
                     'provider', 'is_transferred', 'remote_id',
                     'user__username', 'playlist__name')
    readonly_fields = ('name', 'artist', 'album', 'playlist',
                       'provider', 'is_transferred', 'remote_id')


class CreatedPlaylistModelAdmin(admin.ModelAdmin):
    list_display = 'name', 'status', 'provider', 'user'
    search_fields = 'name', 'provider', 'remote_id', 'user__username'
    readonly_fields = 'name', 'status', 'provider', 'remote_id', 'user'


class SearchErrorTrackModelAdmin(admin.ModelAdmin):
    list_display = 'name', 'provider'
    search_fields = 'provider',


admin.site.register(Playlist, PlaylistModelAdmin)
admin.site.register(PlaylistTrack, PlaylistTrackModelAdmin)
admin.site.register(SearchErrorTrack, SearchErrorTrackModelAdmin)
admin.site.register(CreatedPlaylist, CreatedPlaylistModelAdmin)
