import logging
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable, Iterable, List, Optional

from musicwire.core.exceptions import ValidationError, ProviderResponseError
from musicwire.provider.clients.spotify import Client
from musicwire.provider.datastructures import ClientResult

logger = logging.getLogger(__name__)


class Adapter:
    _executor = ThreadPoolExecutor(max_workers=4)
    saved_tracks_id = "spotify_saved_tracks"

    def __init__(self, token):
        req_data = {
            'base_url': "https://api.spotify.com/v1/",
            'token': token,
        }
        self.spotify_client = Client(**req_data)

    @staticmethod
    def validate_response(response: ClientResult):
        if response.error:
            raise ProviderResponseError(response.error_msg)
        return response.result

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
        self.validate_response(response)

        total_pages = int(response.get('total') / limit) + 1

        request_data = [{'limit': limit, 'offset': offset + limit * page, **kwargs}
                        for page in range(total_pages)]

        return self.collect_concurrently(fn, request_data, fn.__name__)

    @staticmethod
    def get_tracks(tracks: List[dict]) -> List[dict]:
        saved_tracks = []

        for item in tracks:
            for track in item['items']:
                track = track['track']
                track_data = {
                    'track_id': track['id'],
                    'track_album_name': track['album']['name'],
                    'track_name': track['name'],
                    'track_artist': track['artists'][0]['name'],
                    'track_uri': track['uri']
                }
                saved_tracks.append(track_data)

        return saved_tracks

    def saved_tracks(self, limit=50, offset=0) -> Optional[List]:
        """
        Get saved tracks of user.
        """
        tracks = self.collector(self.spotify_client.get_saved_tracks, limit, offset)

        return self.get_tracks(tracks)

    def playlists(self, limit=50, offset=0) -> Optional[List]:
        """
        Get playlists of user.
        """
        user_playlists = []

        playlists = self.collector(self.spotify_client.get_playlists, limit, offset)

        # TODO: check if first loop necessary
        for item in playlists:
            for playlist in item['items']:
                playlist_data = {
                    'playlist_id': playlist['id'],
                    'playlist_name': playlist['name'],
                    'playlist_status': "public" if playlist['public'] else "private",
                    'playlist_content': None
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

    def playlist_tracks(self, playlist_id: str, limit=50, paging=0) -> Optional[List]:
        """
        Get a playlist's tracks.
        """
        data = {'playlist_id': playlist_id}

        tracks = self.collector(self.spotify_client.get_playlist_tracks,
                                limit, paging, **data)

        return self.get_tracks(tracks)

    def create_playlists(self, playlists: list) -> List[dict]:
        """
        Post a new playlist in user account.
        """
        created_playlists = []
        user_id = playlists.pop()

        for playlist in playlists:
            request_data = {
                "name": playlist['playlist_name'],
                "public": playlist.get('privacy_status'),
                "collaborative": playlist.get('collaborative'),
                "description": playlist.get('description')
            }

            response = self.spotify_client.create_a_playlist(user_id, request_data)
            playlist_data = self.validate_response(response)

            try:
                created_playlists.append({
                    "playlist_id": playlist_data['uri'],
                    "playlist_collaborative": playlist_data['collaborative'],  # Need to control this
                    "playlist_description": playlist_data['description'],
                    "playlist_name": playlist_data['name'],
                    "playlist_status": playlist_data['public'],
                })
                logger.info(f"Created: {playlist['playlist_name']}.")
            except TypeError:
                logger.info(f"Fail to create: {playlist['playlist_name']}.")

        return created_playlists

    def add_tracks_to_playlist(self, playlist_id: str, track: list):
        """
        Post tracks to given playlist.
        """
        request_data = {'uris': track}
        response = self.spotify_client.add_tracks_to_playlist(
            playlist_id, request_data
        )
        self.validate_response(response)

        if not response:
            logger.info(f"Spotify insert track fail: {track}")

        return

    def upload_playlist_cover_image(self):
        raise NotImplemented()

    def search(self, search_track: str, search_type: str = 'track') -> List[dict]:
        """
        Search an album, track, artist in spotify to find track to later use in add
        playlist.
        """
        search_results = []
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
            search_results.append({
                'id': search_result[dict_key]['items'][0]['uri'],
                'name': search_result[dict_key]['items'][0]['name'],
                'type': search_result[dict_key]['items'][0]['type'],
            })
        except (KeyError, TypeError):
            logger.info(f"No result found for {search_track}")

        return search_results
