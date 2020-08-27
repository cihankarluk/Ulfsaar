from rest_framework.filters import BaseFilterBackend

from musicwire.music.serializers import (CreatedPlaylistDataSerializer,
                                         PlaylistTrackFilterSerializer,
                                         PlaylistFilterSerializer)


class PlaylistFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_params = {}
        PlaylistFilterSerializer(
            data=request.query_params
        ).is_valid(raise_exception=True)

        name = request.query_params.get("name")
        status = request.query_params.get("status")
        remote_id = request.query_params.get("remote_id")
        content = request.query_params.get("content")
        provider = request.query_params.get("provider")
        is_transferred = request.query_params.get("is_transferred")

        if name:
            filter_params["name__icontains"] = name
        if status:
            filter_params["status__icontains"] = status
        if remote_id:
            filter_params["remote_id"] = remote_id
        if content:
            filter_params["content"] = content
        if is_transferred:
            filter_params["is_transferred"] = is_transferred
        if provider:
            filter_params["provider"] = provider

        queryset = queryset.filter(**filter_params)
        return queryset


class PlaylistTrackFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_params = {}
        PlaylistTrackFilterSerializer(
            data=request.query_params
        ).is_valid(raise_exception=True)

        name = request.query_params.get("name")
        artist = request.query_params.get("artist")
        album = request.query_params.get("album")
        playlist_id = request.query_params.get("playlist_id")
        remote_id = request.query_params.get("remote_id")
        is_transferred = request.query_params.get("is_transferred")
        provider = request.query_params.get("provider")
        playlist_name = request.query_params.get("playlist_name")

        if name:
            filter_params["name__icontains"] = name
        if artist:
            filter_params["artist__icontains"] = artist
        if album:
            filter_params["album__icontains"] = album
        if playlist_id:
            filter_params["playlist__remote_id"] = playlist_id
        if remote_id:
            filter_params["remote_id"] = remote_id
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
