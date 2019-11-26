from django.contrib import admin

from musicwire.provider.spotify.models import Spotify


class SpotifyAdmin(admin.ModelAdmin):
    list_display = ['base_url']

    class Meta:
        model = Spotify


admin.site.register(Spotify, SpotifyAdmin)
