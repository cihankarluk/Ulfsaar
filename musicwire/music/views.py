import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from musicwire.music.models import Playlist, PlaylistTrack
from musicwire.provider.models import Provider
from musicwire.music.serializers import PlaylistsSerializer, TracksSerializer

logger = logging.getLogger(__name__)


class PlaylistView(APIView):
    def post(self, request, *args, **kwargs):
        serialized = PlaylistsSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        source = valid_data['source']
        adapter = Provider.get_provider(source, valid_data['source_token'])

        playlists = adapter.playlists()

        for playlist in playlists:
            Playlist.objects.create(
                name=playlist['playlist_name'],
                status=playlist['playlist_status'],
                remote_id=playlist['playlist_id'],
                content=playlist['playlist_content'],
                provider=source,
                user=request.account
            )

        return Response(playlists, status=200)


class TrackView(APIView):
    def post(self, request, *args, **kwargs):
        serialized = TracksSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        source, playlist_id = valid_data['source'], valid_data['playlist_id']

        try:
            playlist = Playlist.objects.get(remote_id=playlist_id, user=request.account)
        except Playlist.DoesNotExist:
            playlist = None
            logger.info('playlist does not exist for this user.')

        adapter = Provider.get_provider(source, valid_data['source_token'])

        tracks = adapter.playlists_tracks()

        for track in tracks:
            # TODO: need to rename dict keys and use bulk create
            PlaylistTrack.objects.create(
                name=track['track_name'],
                artist=track['track_artist'],
                remote_id=track['id'],
                album=track['track_album_name'],
                playlist=playlist,
                provider=source,
                user=request.account
            )
