import abc
from typing import List


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
