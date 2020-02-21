import logging
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable, Iterable, List, Optional

from musicwire.core.exceptions import AddTracksError, ValidationError
from musicwire.provider.clients.spotify import Client

logger = logging.getLogger(__name__)


class Adapter:
    _executor = ThreadPoolExecutor(max_workers=4)

    def __init__(self, **kwargs):
        req_data = {
            'base_url': "https://api.spotify.com/v1/",
            'token': kwargs['token'],
        }
        self.spotify_client = Client(**req_data)

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
        if not response:
            return []

        total_pages = int(response.get('total') / limit) + 1

        request_data = [{'limit': limit, 'offset': offset + limit * page, **kwargs}
                        for page in range(total_pages)]

        return self.collect_concurrently(fn, request_data, fn.__name__)

    @staticmethod
    def get_saved_tracks(tracks: List[dict]) -> List[dict]:
        saved_tracks = []

        for item in tracks:
            for track in item['items']:
                track = track['track']
                music_data = {
                    'track_id': track['id'],
                    'track_album_name': track['album']['name'],
                    'track_name': track['name'],
                    'track_artist': track['artists'][0]['name'],
                    'track_uri': track['uri']
                }
                saved_tracks.append(music_data)

        return saved_tracks

    def saved_tracks(self, limit=50, offset=0) -> Optional[List]:
        """
        Get saved tracks of user.
        """
        tracks = self.collector(self.spotify_client.get_saved_tracks, limit, offset)

        return self.get_saved_tracks(tracks)

    def playlists(self, limit=50, offset=0) -> Optional[List]:
        """
        Get playlists of user.
        """
        user_playlists = []

        playlists = self.collector(self.spotify_client.get_playlists, limit, offset)

        for item in playlists:
            for playlist in item['items']:
                playlist_data = {
                    'playlist_id': playlist['id'],
                    'playlist_name': playlist['name'],
                    'playlist_public': playlist['public'],
                    'playlist_uri': playlist['uri']
                }
                user_playlists.append(playlist_data)
        return user_playlists

    def albums(self, limit=50, offset=0) -> Optional[List]:
        """
        Get albums of user.
        """
        user_albums = []

        albums = self.collector(self.spotify_client.get_albums, limit, offset)

        for item in albums:
            for album in item['items']:
                album_data = {
                    'album_id': album['album']['id'],
                    'album_name': album['album']['name'],
                    'album_popularity': album['album']['popularity'],
                    'album_uri': album['album']['uri']
                }
                user_albums.append(album_data)
        return user_albums

    def playlist_tracks(self, playlist_id: str, limit=50, offset=0) -> Optional[List]:
        """
        Get a playlist's tracks.
        """
        data = {'playlist_id': playlist_id}

        tracks = self.collector(self.spotify_client.get_playlist_tracks,
                                limit, offset, **data)

        return self.get_saved_tracks(tracks)

    def create_playlist(self, user_id: str, **kwargs) -> Optional[dict]:
        """
        Post a new playlist in user account.
        """
        request_data = {
            "name": kwargs['name'],
            "public": kwargs.get('public'),
            "collaborative": kwargs.get('collaborative'),
            "description": kwargs.get('description')
        }

        response = self.spotify_client.create_a_playlist(user_id, request_data)
        if not response:
            return

        user_new_playlist = {
            "playlist_id": response['id'],
            "playlist_collaborative": response['collaborative'],
            "playlist_description": response['description'],
            "playlist_name": response['name'],
            "playlist_public": response['public'],
            "playlist_uri": response['uri']
        }
        return user_new_playlist

    def add_tracks_to_playlist(self, playlist_id: str, **kwargs) -> bool:
        """
        Post tracks to given playlist. 100 tracks can be added in one time according to
        Spotify api. To avoid possible losses while adding tracks, set limit to 75 to
        divide into chunks to add all tracks as supposed to.
        """
        tracks = kwargs['tracks']
        chunks = [tracks[index:index + 75] for index in range(0, len(tracks), 75)]
        for chunk in chunks:
            request_data = {'uris': chunk}
            response = self.spotify_client.add_tracks_to_playlist(playlist_id,
                                                                  request_data)
            if not response:
                raise AddTracksError('Error while adding tracks into playlist.')
        return True

    def upload_playlist_cover_image(self):
        raise NotImplemented()

    def search(self, request_data: dict) -> Optional[dict]:
        """
        Search a album, track, artist in spotify to find track to later use in add
        playlist.
        """
        search_result = {}

        response = self.spotify_client.search(request_data)
        if not response:
            return

        dict_key, *_ = response
        # Spotify returns first dict key as album or track or artist which depends on
        # search request. This dict_key can be taken from request data but ...

        try:
            search_result = {
                'id': response[dict_key]['items'][0]['id'],
                'name': response[dict_key]['items'][0]['name'],
                'type': response[dict_key]['items'][0]['type'],
                'uri': response[dict_key]['items'][0]['uri']
            }
        except KeyError:
            logger.info(f"No result found for {request_data['q']}")

        return search_result
