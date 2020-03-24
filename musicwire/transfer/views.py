import logging
from typing import List

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView

from musicwire.provider.helpers import import_provider_class
from musicwire.transfer.serializers import TransferPlaylistSerializer

logger = logging.getLogger(__name__)


class TransferPlaylistsView(APIView):
    @staticmethod
    def get_provider(provider: str, token: str):
        """
        Get interested Adapter.
        """
        # TODO: need to check return type
        provider_module = import_provider_class(provider)
        adapter = provider_module(token=token)
        return adapter

    @staticmethod
    def cache_playlist_tracks(adapter, playlists: list) -> bool:
        """
        Cache all playlist tracks according to their playlist names. Later will
        using creating playlist and insert playlist tracks. Returns always true
        since we do not interrupt if any problem occur while getting tracks.
        """
        for playlist in playlists:
            playlist_name = playlist['playlist_name']
            playlist_id = playlist['playlist_id']
            tracks = adapter.playlist_tracks(playlist_id=playlist_id)

            if not tracks:
                logger.info(f"Problem with getting tracks of {playlist_name}.")

            cache.set(playlist_name, tracks, settings.TRACK_CACHE_TIME)
        return True

    @staticmethod
    def add_tracks_to_playlists(adapter, created_playlists: list):
        for created_playlist in created_playlists:
            search_tracks = cache.get(created_playlist['playlist_name'])
            for track in search_tracks:
                search_results = adapter.search(track['track_name'])
                playlist_id = created_playlist['playlist_id']
                adapter.add_tracks_to_playlist(
                    playlist_id=playlist_id,
                    track=search_results['id']
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
            playlists = []
            playlists.append({'playlist_name': 'saved_tracks', 'playlist_status': False})

        to_provider = valid_data['to_']
        to_token = valid_data['to_token']
        to_adapter = self.get_provider(to_provider, to_token)

        if to_provider == 'spotify':
            playlists.append(valid_data['user_id'])

        # created_playlists = to_adapter.create_playlists(playlists)
        created_playlists = [{'playlist_id': 'PLC7MwgN4I2dURJorFgMe7Dzg6SgTe9-wX',
                              'playlist_collaborative': None,
                              'playlist_description': '',
                              'playlist_name': 'saved_tracks',
                              'playlist_status': 'private'}]
        self.add_tracks_to_playlists(
            adapter=to_adapter,
            created_playlists=created_playlists
        )
