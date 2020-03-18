import logging
from typing import Optional

from musicwire.provider.clients.youtube import Client

logger = logging.getLogger(__name__)


class Adapter:
    def __init__(self, token):
        req_data = {
            'base_url': "https://www.googleapis.com/youtube/v3/",
            "token": token
        }
        self.youtube_client = Client(**req_data)
        self.part = 'snippet, status, contentDetails'

    def playlists(self):
        """
        Get playlists of user.
        """
        user_playlists = []

        request_data = {
            'part': self.part,
            'mine': True
        }

        playlists = self.youtube_client.get_playlists(**request_data)

        for playlist in playlists['items']:
            playlist_data = {
                'playlist_id': playlist['id'],
                'playlist_name': playlist['snippet']['title'],
                'playlist_status': playlist['status']['privacyStatus'],
                'playlist_content': playlist['contentDetails']['itemCount']
            }
            user_playlists.append(playlist_data)
        return user_playlists

    def playlist_tracks(self, playlist_id: str, limit=50, page_token=None):
        """
        Get playlist's tracks.
        """
        user_tracks = []

        params = {
            'maxResults': limit,
            'part': self.part,
            'playlistId': playlist_id,
            'pageToken': page_token
        }

        while True:
            tracks = self.youtube_client.get_playlist_tracks(**params)
            for track in tracks['items']:
                track_data = {
                    'track_id': track['id'],
                    'track_album_name': None,
                    'track_name': track['snippet']['title'],
                    'track_artist': None,
                }
                user_tracks.append(track_data)
            next_page_token = tracks.get('nextPageToken')

            if not next_page_token:
                break
            params['pageToken'] = next_page_token
        return user_tracks

    def create_playlist(self, name, **kwargs) -> Optional[dict]:
        """
        Post a new playlist in user account.
        """
        params = {
            'part': self.part
        }
        request_data = {
            "snippet": {
                "title": name,
                "description": kwargs.get('description')
            },
            "status": {
                "privacyStatus": kwargs.get('privacy_status')  # private, public
            }
        }

        response = self.youtube_client.create_a_playlist(params, request_data)
        if not response:
            return

        user_new_playlist = {
            "playlist_id": response['id'],
            "playlist_collaborative": None,
            "playlist_description": response['snippet']['description'],
            "playlist_name": response['title'],
            "playlist_status": response['status']['privacyStatus']
        }
        return user_new_playlist

    def add_tracks_to_playlist(self, playlist_id: str, tracks: list) -> list:
        """
        Post tracks to given playlist.
        """
        fail_tracks = []

        params = {
            'part': self.part
        }
        request_data = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {}
            }
        }

        for track in tracks:
            request_data['snippet']['resourceId']['videoId'] = track
            response = self.youtube_client.add_tracks_to_playlist(
                params=params, request_data=request_data)
            if not response:
                fail_tracks.append(track)

        if fail_tracks:
            logger.info(f"Youtube insert fails: {fail_tracks}")

        return fail_tracks

    def search(self, search_tracks: list) -> Optional[list]:
        """
        Search for given tracks and append results to later use in add tracks to
        playlist.
        """
        search_results = []

        params = {
            'part': 'snippet'
        }

        for track in search_tracks:
            params['q'] = track
            response = self.youtube_client.search(params)
            if not response:
                return
            try:
                search_results.append({
                    'id': response['items'][0]['id']['videoId'],
                    'name': response['items'][0]['title'],
                    'type': None,
                })
            except KeyError:
                logger.info(f"No result found for {track}")

        return search_results

