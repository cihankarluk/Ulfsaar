import logging
import re
from typing import List

from musicwire.provider.adapters.base import BaseAdapter
from musicwire.provider.clients.youtube import Client

logger = logging.getLogger(__name__)


class Adapter(BaseAdapter):
    def __init__(self, token):
        req_data = {
            'base_url': "https://www.googleapis.com/youtube/v3/",
            "token": token
        }
        self.youtube_client = Client(**req_data)
        self.part = 'snippet, status, contentDetails'

    @staticmethod
    def simplify_track_title(title: str):
        characters_to_remove = "[!()@-]"
        strings_to_remove = "Official.Video"
        title = re.sub(characters_to_remove, "", title)
        title = re.sub(strings_to_remove, "", title)
        return title

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

    def playlist_tracks(self, playlist_id: str, limit=50, paging=None):
        """
        Get playlist's tracks.
        """
        user_tracks = []

        params = {
            'maxResults': limit,
            'part': self.part,
            'playlistId': playlist_id,
            'pageToken': paging
        }

        while True:
            # Cannot be done with async or threads due to google turns each page
            # with page token
            tracks = self.youtube_client.get_playlist_tracks(**params)

            for track in tracks['items']:
                track_data = {
                    'track_id': track['id'],
                    'track_album_name': None,
                    'track_name': self.simplify_track_title(track['snippet']['title']),
                    'track_artist': None,
                }
                user_tracks.append(track_data)
            next_page_token = tracks.get('nextPageToken')

            if not next_page_token:
                break
            params['pageToken'] = next_page_token
        return user_tracks

    def create_playlists_selection(self):
        # TODO: need to write this part to give chose option for user to which playlists
        #  will be added.
        raise NotImplemented()

    def create_playlists(self, playlists: list) -> List[dict]:
        """
        Post a new playlists in user account. Max create playlist limit is set to
         10 per day.
        """
        created_playlists = []
        params = {'part': self.part}

        if len(playlists) > 10:
            logger.info(f"Only 10 playlists will be inserted due "
                        f"to google block more then 10 playlist insertion per day. "
                        f"Playlists to be added are: {playlists[:10]}")

        for playlist in playlists[:10]:
            privacy_status: bool = playlist.get('privacy_status')
            request_data = {
                "snippet": {
                    "title": playlist['playlist_name'],
                    "description": playlist.get('description')
                },
                "status": {
                    "privacyStatus": 'public' if privacy_status else 'private'
                }
            }

            playlist_data = self.youtube_client.create_a_playlist(params, request_data)

            try:
                created_playlists.append({
                    "playlist_id": playlist_data['id'],
                    "playlist_collaborative": None,
                    "playlist_description": playlist_data['snippet']['description'],
                    "playlist_name": playlist_data['snippet']['title'],
                    "playlist_status": playlist_data['status']['privacyStatus']
                })
                logger.info(f"Created: {playlist['playlist_name']}.")
            except TypeError:
                logger.info(f"Fail to create: {playlist['playlist_name']}.")

        return created_playlists

    def add_track_to_playlist(self, playlist_id: str, track_id: str):
        """
        Post tracks to given playlist.
        """
        params = {
            'part': self.part
        }
        request_data = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": track_id
                }
            }
        }

        self.youtube_client.add_tracks_to_playlist(
            params=params, request_data=request_data
        )

        return

    def search(self, search_track: str, search_type: str = None) -> dict:
        """
        Search for given tracks and append results to later use in add tracks to
        playlist.
        """
        search_response = {}

        params = {
            'part': 'snippet',
            'q': search_track,
        }

        search_result = self.youtube_client.search(params)

        try:
            search_response = {
                'id': search_result['items'][0]['id']['videoId'],
                'name': search_result['items'][0]['snippet']['title'],
                'type': None,
            }
        except (KeyError, TypeError):
            logger.info(f"No result found for {search_track}")

        return search_response
