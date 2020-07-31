import logging

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from musicwire.music.filters import PlaylistTrackFilter
from musicwire.music.models import Playlist, PlaylistTrack
from musicwire.provider.models import Provider
from musicwire.music.serializers import PlaylistPostSerializer, TrackPostSerializer, \
    PlaylistSerializer, TrackSerializer, CreatePlaylistSerializer, \
    AddPlaylistTrackSerializer

logger = logging.getLogger(__name__)


class PlaylistView(generics.ListAPIView):
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        playlists = Playlist.objects.filter(user=self.request.account)
        return playlists

    def post(self, request, *args, **kwargs):
        serialized = PlaylistPostSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        source = valid_data['source']
        adapter = Provider.get_provider(source, valid_data['source_token'])

        playlists = adapter.playlists()
        if source == Provider.SPOTIFY:
            playlists.append({
                "playlist_id": adapter.saved_tracks_id,
                "playlist_name": "saved_tracks",
                "playlist_status": "public",
                "playlist_content": None,
            })

        db_playlist = Playlist.objects.filter(
            user=request.account
        ).values_list('remote_id', flat=True)

        objs = [Playlist(
            name=playlist['playlist_name'],
            status=playlist['playlist_status'],
            remote_id=playlist['playlist_id'],
            content=playlist['playlist_content'],
            provider=source,
            user=request.account
        ) for playlist in playlists if playlist['playlist_id'] not in db_playlist]

        Playlist.objects.bulk_create(objs)

        return Response(playlists, status=200)


class PlaylistTrackView(generics.ListAPIView):
    serializer_class = TrackSerializer
    filter_backends = [PlaylistTrackFilter]

    def get_queryset(self):
        request = self.request
        tracks = PlaylistTrack.objects.select_related('playlist').filter(
            user=request.account
        )
        return tracks

    def post(self, request, *args, **kwargs):
        serialized = TrackPostSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        source, playlist_id = valid_data['source'], valid_data['playlist_id']

        try:
            playlist = Playlist.objects.get(remote_id=playlist_id, user=request.account)
        except Playlist.DoesNotExist:
            playlist = None
            logger.info('playlist does not exist for this user.')

        adapter = Provider.get_provider(source, valid_data['source_token'])

        if playlist_id == "spotify_saved_tracks":
            tracks = adapter.saved_tracks()
        else:
            tracks = adapter.playlist_tracks(playlist_id=playlist_id)

        db_tracks = PlaylistTrack.objects.filter(
            user=request.account
        ).values_list('remote_id', flat=True)

        objs = [PlaylistTrack(
            name=track['track_name'],
            artist=track['track_artist'],
            remote_id=track['track_id'],
            album=track['track_album_name'],
            playlist=playlist,
            provider=source,
            user=request.account
        ) for track in tracks if track['track_id'] not in db_tracks]

        PlaylistTrack.objects.bulk_create(objs)

        return Response(tracks, status=200)


class CreatePlaylistView(APIView):
    # TODO: may add model to view for created playlists.
    serializer_class = CreatePlaylistSerializer

    def post(self, request, *args, **kwargs):
        serialized = self.serializer_class(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        end = valid_data['end']
        adapter = Provider.get_provider(end, valid_data['end_token'])

        request_data = {
            "playlist_name": valid_data["playlist_name"],
            "privacy_status": valid_data.get("privacy_status"),
            "collaborative": valid_data.get("collaborative"),
            "description": valid_data.get("description"),
        }

        if end == Provider.SPOTIFY:
            request_data["user_id"] = valid_data["user_id"]

        playlist = adapter.create_playlist(request_data)

        return Response(playlist, status=200)


class AddTrackToPlaylistView(APIView):
    serializer_class = AddPlaylistTrackSerializer

    def post(self, request, *args, **kwargs):
        serialized = AddPlaylistTrackSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        adapter = Provider.get_provider(valid_data['end'], valid_data['end_token'])
        adapter.add_track_to_playlist(valid_data['playlist_id'], valid_data['track_id'])

        return Response(status=201)
