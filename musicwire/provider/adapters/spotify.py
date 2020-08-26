import logging
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable, Iterable, List, Optional

from musicwire.core.exceptions import ValidationError, ProviderResponseError
from musicwire.music.models import Playlist, PlaylistTrack, CreatedPlaylist
from musicwire.provider.adapters.base import BaseAdapter
from musicwire.provider.clients.spotify import Client
from musicwire.provider.datastructures import ClientResult
from musicwire.provider.models import Provider

logger = logging.getLogger(__name__)


class Adapter(BaseAdapter):
    _executor = ThreadPoolExecutor(max_workers=4)
    saved_tracks_id = "spotify_saved_tracks"

    def __init__(self, token, user):
        req_data = {
            'base_url': "https://api.spotify.com/v1/",
            'token': token,
        }
        self.spotify_client = Client(**req_data)
        self.user = user

    @staticmethod
    def validate_response(response: ClientResult):
        if response.error:
            raise ProviderResponseError(response.error_msg)
        return response.result

    @staticmethod
    def status_control(playlist_data):
        return "public" if playlist_data['public'] else "private"

    def collect_concurrently(
            self, fn: Callable, collection: Iterable, title=None
    ) -> List:
        """
        Maps each elements of a collection with a function and processes
        the calls concurrently.
        """
        results = []
        waiting_task = [self._executor.submit(fn, product) for product in collection]

        total = len(collection)
        for i, future in enumerate(as_completed(waiting_task), start=1):
            result = future.result()
            results.append(result)
            percentage = int(i / total * 100)
            print(f"{title}:{i:3}/{total} {percentage}%", end="\r")
        return results

    def collector(
            self, fn: Callable, limit: int, offset: int, **kwargs
    ) -> list:
        """
        Iterate through all pages and return list of results.
        """
        if limit > 50:
            # Spotify limit for response count.
            raise ValidationError('Invalid limit. Max limit is 50.')

        request_data = {
            "limit": limit,
            "offset": offset,
            **kwargs
        }

        response = fn(request_data=request_data)
        # TODO: Might concatenate this response with thread responses to avoid
        #  redundant request
        response = self.validate_response(response)

        total_pages = int(response.get('total') / limit) + 1

        request_data = [{'limit': limit, 'offset': offset + limit * page, **kwargs}
                        for page in range(total_pages)]

        return self.collect_concurrently(fn, request_data, fn.__name__)

    def get_tracks(self, tracks: List[dict], playlist_id: str) -> List[object]:
        finished_tracks = []

        playlist = self.get_db_playlist(playlist_id=playlist_id, user=self.user)
        db_tracks = self.get_db_tracks(user=self.user)

        for item in tracks:
            objs = [PlaylistTrack(
                name=track['track']['name'],
                artist=track['track']['artists'][0]['name'],
                remote_id=track['track']['uri'],
                album=track['track']['album']['name'],
                playlist=playlist,
                provider=Provider.SPOTIFY,
                user=self.user
            ) for track in item['items'] if track['track']['uri'] not in db_tracks]
            PlaylistTrack.objects.bulk_create(objs)
            finished_tracks.append(objs)

        return finished_tracks

    def saved_tracks(self, playlist_id: str, limit=50, offset=0) -> Optional[List]:
        """
        Get saved tracks of user.
        """
        tracks = []
        responses: list = self.collector(self.spotify_client.get_saved_tracks, limit, offset)

        for response in responses:
            tracks.append(self.validate_response(response))

        return self.get_tracks(tracks=tracks, playlist_id=playlist_id)

    def playlists(self, limit=50, offset=0) -> list:
        """
        Get playlists of user.
        """
        objs, playlists = [], []

        responses: list = self.collector(self.spotify_client.get_playlists, limit, offset)

        for response in responses:
            playlists.append(self.validate_response(response))

        db_playlist = self.get_db_playlists(self.user)

        # TODO: check if first loop necessary
        for item in playlists:
            objs = [Playlist(
                name=playlist['name'],
                status=self.status_control(playlist),
                remote_id=playlist['id'],
                content=None,
                provider=Provider.SPOTIFY,
                user=self.user
            ) for playlist in item['items'] if playlist['id'] not in db_playlist]

        Playlist.objects.bulk_create(objs)

        return objs

    def albums(self, limit=50, offset=0) -> Optional[List]:
        """
        Get albums of user.
        """
        user_albums, albums = [], []

        responses = self.collector(self.spotify_client.get_albums, limit, offset)

        for response in responses:
            albums.append(self.validate_response(response))

        for item in albums:
            for album in item['items']:
                album_data = {
                    'album_id': album['album']['uri'],
                    'album_name': album['album']['name'],
                    'album_popularity': album['album']['popularity'],
                }
                user_albums.append(album_data)
        return user_albums

    def playlist_tracks(self, playlist_id: str, limit=50, paging=0) -> Optional[List]:
        """
        Get a playlist's tracks.
        """
        tracks = []
        data = {'playlist_id': playlist_id}

        responses = self.collector(self.spotify_client.get_playlist_tracks,
                                   limit, paging, **data)

        for response in responses:
            tracks.append(self.validate_response(response))

        return self.get_tracks(tracks=tracks, playlist_id=playlist_id)

    def create_playlist(self, playlist_data: dict) -> dict:
        """
        Post a new playlist in user account.
        """
        user_id = playlist_data.pop('user_id')

        request_data = {
            "name": playlist_data['playlist_name'],
            "public": playlist_data.get('privacy_status'),
            "description": playlist_data.get('description')
        }

        response = self.spotify_client.create_a_playlist(user_id, request_data)
        playlist_data = self.validate_response(response)

        created_playlist = {
            "name": playlist_data['name'],
            "status": self.status_control(playlist_data),
            "remote_id": playlist_data['id'],
            "provider": Provider.SPOTIFY,
            "user": self.user
        }
        CreatedPlaylist.objects.create(**created_playlist)
        created_playlist.pop("user")

        return created_playlist

    def add_track_to_playlist(self, playlist_id: str, track_id: str):
        """
        Post tracks to given playlist.
        """
        request_data = {'uris': [track_id]}
        response = self.spotify_client.add_tracks_to_playlist(
            playlist_id, request_data
        )
        self.validate_response(response)

        return response

    def upload_playlist_cover_image(self):
        raise NotImplemented()

    def search(self, search_track: str, search_type: str = 'track') -> dict:
        """
        Search an album, track, artist in spotify to find track to later use in add
        playlist.
        """
        params = {
            'type': search_type,
            'q': search_track
        }

        response = self.spotify_client.search(params=params)
        search_result = self.validate_response(response)

        # Spotify returns first dict key as album or track or artist which depends on
        # search request. This dict_key can be taken from request data but ...
        dict_key, *_ = search_result

        try:
            search_response = {
                'id': search_result[dict_key]['items'][0]['uri'],
                'name': search_result[dict_key]['items'][0]['name'],
                'type': search_result[dict_key]['items'][0]['type'],
            }
        except (KeyError, TypeError):
            search_response = {}
            self.create_search_error(
                search_track=search_track,
                search_result=search_result,
                user=self.user,
                provider=Provider.SPOTIFY
            )

        return search_response
