import itertools
import logging
from typing import List

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from musicwire.core.exceptions import (AllPlaylistsAlreadyProcessed,
                                       AllTracksAlreadyProcessed)
from musicwire.music.filters import CreatedPlaylistFilter, PlaylistTrackFilter, \
    PlaylistFilter
from musicwire.music.models import (CreatedPlaylist, Playlist, PlaylistTrack,
                                    SearchErrorTrack)
from musicwire.music.serializers import (AddPlaylistTrackSerializer,
                                         CreatedPlaylistSerializer,
                                         CreatePlaylistSerializer,
                                         PlaylistPostSerializer,
                                         PlaylistSerializer,
                                         PulledPlaylistSerializer,
                                         SearchSerializer, TrackPostSerializer,
                                         TrackSerializer, SearchErrorSerializer)
from musicwire.provider.models import Provider

logger = logging.getLogger(__name__)


class PlaylistView(generics.ListAPIView):
    serializer_class = PlaylistSerializer
    filter_backends = [PlaylistFilter]

    def get_queryset(self):
        playlists = Playlist.objects.filter(user=self.request.account)
        return playlists

    def post(self, request, *args, **kwargs):
        """
        This method pull all playlists from provider.
        """
        serialized = PlaylistPostSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        source = valid_data['source']
        adapter = Provider.get_provider(
            provider=source,
            token=valid_data['source_token'],
            user=request.account
        )

        playlists: list = adapter.playlists()
        if source == Provider.SPOTIFY:
            try:
                Playlist.objects.get(
                    remote_id=adapter.saved_tracks_id,
                    user=request.account
                )
            except Playlist.DoesNotExist:
                saved_tracks_playlist = Playlist(
                        name="saved_tracks",
                        status="private",
                        remote_id=adapter.saved_tracks_id,
                        content=None,
                        provider=Provider.SPOTIFY,
                        user=request.account
                )
                saved_tracks_playlist.save()
                playlists.append(saved_tracks_playlist)

        if not any(playlists):
            raise AllPlaylistsAlreadyProcessed(
                "All playlist on this account already processed."
            )

        serialized = PulledPlaylistSerializer({"playlists": playlists})
        return Response(serialized.data, status=200)


class PlaylistTrackView(generics.ListAPIView):
    serializer_class = TrackSerializer
    filter_backends = [PlaylistTrackFilter]

    def get_queryset(self):
        tracks = PlaylistTrack.objects.select_related('playlist').filter(
            user=self.request.account
        )
        return tracks

    def post(self, request, *args, **kwargs):
        """
        This method pull all playlist tracks from provider for given playlist.
        """
        serialized = TrackPostSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        source, playlist_id = valid_data['source'], valid_data['playlist_id']

        adapter = Provider.get_provider(
            provider=source,
            token=valid_data['source_token'],
            user=request.account
        )

        if source == Provider.SPOTIFY and playlist_id == "spotify_saved_tracks":
            tracks: List[list] = adapter.saved_tracks(playlist_id=playlist_id)
        else:
            tracks: List[list] = adapter.playlist_tracks(playlist_id=playlist_id)

        if not any(tracks):
            raise AllTracksAlreadyProcessed(
                "All tracks on this playlist already processed."
            )

        # We get list of lists. Due to this condition need to flatten that list.
        merged = list(itertools.chain(*tracks))
        serialized = TrackSerializer(merged, many=True)
        return Response(serialized.data, status=200)


class CreatePlaylistView(generics.ListAPIView):
    serializer_class = CreatedPlaylistSerializer
    filter_backends = [CreatedPlaylistFilter]

    def get_queryset(self):
        created_playlists = CreatedPlaylist.objects.filter(
            user=self.request.account
        )
        return created_playlists

    def post(self, request, *args, **kwargs):
        serialized = CreatePlaylistSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        adapter = Provider.get_provider(
            provider=valid_data["end"],
            token=valid_data['end_token'],
            user=request.account
        )

        playlist = adapter.create_playlist(valid_data)

        return Response(playlist, status=200)


class AddTrackToPlaylistView(APIView):
    serializer_class = AddPlaylistTrackSerializer

    def post(self, request, *args, **kwargs):
        serialized = self.serializer_class(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        adapter = Provider.get_provider(
            provider=valid_data['end'],
            token=valid_data['end_token'],
            user=request.account
        )
        adapter.add_track_to_playlist(valid_data['playlist_id'], valid_data['track_id'])

        return Response(status=201)


class SearchView(generics.ListCreateAPIView):
    serializer_class = SearchErrorSerializer
    queryset = SearchErrorTrack.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.account)

    def post(self, request, *args, **kwargs):
        serialized = SearchSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        adapter = Provider.get_provider(
            provider=valid_data['source'],
            token=valid_data['source_token'],
            user=request.account
        )
        response = adapter.search(valid_data['track_name'])

        return Response(response, status=200)
