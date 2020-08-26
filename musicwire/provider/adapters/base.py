import abc
import logging
from typing import List, Optional

from musicwire.music.models import Playlist, PlaylistTrack, SearchErrorTrack

logger = logging.getLogger(__name__)


class BaseAdapter(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def playlists(self):
        raise NotImplemented()

    @abc.abstractmethod
    def playlist_tracks(self, playlist_id: str, paging, limit=50):
        raise NotImplemented()

    @abc.abstractmethod
    def create_playlist(self, playlist_data: dict) -> dict:
        raise NotImplemented()

    @abc.abstractmethod
    def add_track_to_playlist(self, playlist_id: str, track: str):
        raise NotImplemented()

    @abc.abstractmethod
    def search(self, search_track: str, search_type: str) -> List[dict]:
        raise NotImplemented()

    @staticmethod
    def get_db_playlist(playlist_id: str, user: object) -> Optional[object]:
        try:
            playlist = Playlist.objects.get(remote_id=playlist_id, user=user)
        except Playlist.DoesNotExist:
            playlist = None
            logger.info('Playlist does not exist for this user.')

        return playlist

    @staticmethod
    def get_db_tracks(user: object) -> list:
        db_tracks = PlaylistTrack.objects.filter(
            user=user
        ).values_list('remote_id', flat=True)

        return db_tracks

    @staticmethod
    def get_db_playlists(user: object) -> list:
        db_playlists = Playlist.objects.filter(
            user=user
        ).values_list('remote_id', flat=True)

        return db_playlists

    @staticmethod
    def create_search_error(search_track: str, search_result, user: object, provider: str):
        SearchErrorTrack.objects.create(
            name=search_track,
            response=search_result,
            provider=provider,
            user=user
        )
