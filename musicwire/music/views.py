import logging

from rest_framework import generics
from rest_framework.response import Response

from musicwire.music.models import Playlist, PlaylistTrack
from musicwire.provider.models import Provider
from musicwire.music.serializers import PlaylistPostSerializer, TrackPostSerializer, \
    PlaylistSerializer, TrackSerializer

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

        for playlist in playlists:
            Playlist.objects.get_or_create(
                name=playlist['playlist_name'],
                status=playlist['playlist_status'],
                remote_id=playlist['playlist_id'],
                content=playlist['playlist_content'],
                provider=source,
                user=request.account
            )

        return Response(playlists, status=200)


class TrackView(generics.ListAPIView):
    serializer_class = TrackSerializer

    def get_queryset(self):
        request = self.request
        query_params = request.query_params
        tracks = PlaylistTrack.objects.select_related('playlist').filter(
            user=request.account,
            playlist__remote_id=query_params.get('playlist_id')
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

        for track in tracks:
            # TODO: need to rename dict keys and use bulk create
            PlaylistTrack.objects.get_or_create(
                name=track['track_name'],
                artist=track['track_artist'],
                remote_id=track['track_id'],
                album=track['track_album_name'],
                playlist=playlist,
                provider=source,
                user=request.account
            )

        return Response(tracks, status=200)
