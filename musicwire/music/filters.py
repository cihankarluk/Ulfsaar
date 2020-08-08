from rest_framework.filters import BaseFilterBackend

from musicwire.music.serializers import PlaylistTrackFilterSerializer, \
    CreatedPlaylistDataSerializer


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
        playlist_name = request.query_params.get("playlist_name")

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
        if playlist_name:
            filter_params["playlist__name"] = playlist_name

        queryset = queryset.filter(**filter_params)
        return queryset


class CreatedPlaylistFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_params = {}
        CreatedPlaylistDataSerializer(
            data=request.query_params
        ).is_valid(raise_exception=True)

        name = request.query_params.get("name")
        status = request.query_params.get("status")
        playlist_id = request.query_params.get("playlist_id")
        provider = request.query_params.get("provider")

        if name:
            filter_params["name__icontains"] = name
        if status:
            filter_params["status"] = status
        if playlist_id:
            filter_params["remote_id"] = playlist_id
        if provider:
            filter_params["provider"] = provider

        queryset = queryset.filter(**filter_params)
        return queryset
