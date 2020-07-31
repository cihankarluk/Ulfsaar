from rest_framework.filters import BaseFilterBackend

from musicwire.music.serializers import PlaylistTrackFilterSerializer


class PlaylistTrackFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_params = {}
        PlaylistTrackFilterSerializer(
            data=request.query_params
        ).is_valid(raise_exception=True)

        playlist_id = request.query_params.get("playlist_id")
        name = request.query_params.get("name")
        album = request.query_params.get("album")
        is_transferred = request.query_params.get("is_transferred")
        provider = request.query_params.get("provider")

        if playlist_id:
            filter_params["playlist__remote_id"] = playlist_id
        if name:
            filter_params["name__icontains"] = name
        if album:
            filter_params["album__icontains"] = album
        if is_transferred:
            filter_params["is_transferred"] = is_transferred
        if provider:
            filter_params["provider"] = provider

        queryset = queryset.filter(**filter_params)
        return queryset
