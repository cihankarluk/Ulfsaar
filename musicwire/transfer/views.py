import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.views import APIView

from musicwire.transfer.serializers import TransferPlaylistSerializer

logger = logging.getLogger(__name__)


class TransferPlaylistsView(APIView):
    @staticmethod
    def cache_playlist_tracks(adapter, playlists: list) -> bool:
        """
        Cache all playlist tracks according to their playlist names. Later will
        using creating playlist and insert playlist tracks. Returns always true
        since we do not interrupt if any problem occur while getting tracks.
        """
        for playlist in playlists:
            playlist_name = playlist['playlist_name']

            if cache.get(playlist_name):
                continue

            tracks = adapter.playlist_tracks(playlist_id=playlist['playlist_id'])

            if not tracks:
                logger.info(f"Problem with getting tracks of {playlist_name}.")

            cache.set(playlist_name, tracks, settings.TRACK_CACHE_TIME)
        return True

    @staticmethod
    def add_tracks_to_playlists(adapter, created_playlists: list):
        for created_playlist in created_playlists:
            search_tracks = cache.get(created_playlist['playlist_name'])
            for track in search_tracks:
                search_result = adapter.search(track['track_name'])
                if not search_result:
                    continue

                adapter.add_tracks_to_playlist(
                    playlist_id=created_playlist['playlist_id'],
                    track=search_result['id']
                )

    def post(self, request, *args, **kwargs):
        serialized = TransferPlaylistSerializer(data=self.request.data)
        serialized.is_valid(raise_exception=True)
        valid_data = serialized.validated_data

        from_provider = valid_data['from_']
        from_token = valid_data['from_token']
        from_adapter = self.get_provider(from_provider, from_token)

        playlists = from_adapter.playlists()
        self.cache_playlist_tracks(adapter=from_adapter, playlists=playlists)

        if from_provider == 'spotify':
            # Spotify does not provider saved tracks as playlist.
            saved_tracks = from_adapter.saved_tracks()
            cache.set(f"saved_tracks", saved_tracks, settings.TRACK_CACHE_TIME)
            playlists = []  # TODO: this will be removed
            playlists.append({'playlist_name': 'saved_tracks', 'playlist_status': False})

        to_provider = valid_data['to_']
        to_token = valid_data['to_token']
        to_adapter = self.get_provider(to_provider, to_token)

        if to_provider == 'spotify':
            playlists.append(valid_data['user_id'])

        # created_playlists = to_adapter.create_playlists(playlists)
        created_playlists = [{'playlist_id': 'PLQBAidSrPHH_oh0NhuNwlawcK-lmrD5zY',
                              'playlist_collaborative': None,
                              'playlist_description': '',
                              'playlist_name': 'saved_tracks',
                              'playlist_status': 'private'}]
        self.add_tracks_to_playlists(
            adapter=to_adapter,
            created_playlists=created_playlists
        )

        x = {"success": True}
        return HttpResponse(**x, status=200)
