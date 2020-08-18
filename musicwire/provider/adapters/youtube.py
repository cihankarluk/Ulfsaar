import logging
import re
from typing import List

from musicwire.core.exceptions import ProviderResponseError
from musicwire.music.models import Playlist, PlaylistTrack, CreatedPlaylist
from musicwire.provider.adapters.base import BaseAdapter
from musicwire.provider.clients.youtube import Client
from musicwire.provider.datastructures import ClientResult
from musicwire.provider.models import Provider

logger = logging.getLogger(__name__)


class Adapter(BaseAdapter):
    def __init__(self, token, user):
        req_data = {
            'base_url': "https://www.googleapis.com/youtube/v3/",
            "token": token
        }
        self.youtube_client = Client(**req_data)
        self.part = 'snippet, status, contentDetails'
        self.user = user

    @staticmethod
    def simplify_track_title(title: str):
        characters_to_remove = "[!()@-]"
        strings_to_remove = "Official.Video"
        title = re.sub(characters_to_remove, "", title)
        title = re.sub(strings_to_remove, "", title)
        return title

    @staticmethod
    def validate_response(response: ClientResult):
        if response.error:
            raise ProviderResponseError(response.error_msg)
        return response.result

    def playlists(self):
        """
        Get playlists of user.
        """
        params = {
            'part': self.part,
            'mine': True
        }

        response = self.youtube_client.get_playlists(params=params)
        playlists = self.validate_response(response)

        db_playlist = self.get_db_playlists(self.user)

        objs = [Playlist(
            name=playlist['snippet']['title'],
            status=playlist['status']['privacyStatus'],
            remote_id=playlist['id'],
            content=playlist['contentDetails']['itemCount'],
            provider=Provider.YOUTUBE,
            user=self.user
        ) for playlist in playlists['items'] if playlist['id'] not in db_playlist]

        Playlist.objects.bulk_create(objs)

        return objs

    def playlist_tracks(self, playlist_id: str, limit=50, paging=None) -> List[object]:
        """
        Get playlist's tracks.
        """
        finished_tracks = []

        params = {
            'maxResults': limit,
            'part': self.part,
            'playlistId': playlist_id,
            'pageToken': paging
        }

        playlist = self.get_db_playlist(playlist_id=playlist_id, user=self.user)
        db_tracks = self.get_db_tracks(user=self.user)

        while True:
            # Cannot be done with async or threads due to google turns each page
            # with page token
            response = self.youtube_client.get_playlist_tracks(params=params)

            tracks = self.validate_response(response)

            objs = [PlaylistTrack(
                name=self.simplify_track_title(track['snippet']['title']),
                artist=None,
                remote_id=track["snippet"]["resourceId"]["videoId"],
                album=None,
                playlist=playlist,
                provider=Provider.YOUTUBE,
                user=self.user
            ) for track in tracks['items'] if track['id'] not in db_tracks]
            PlaylistTrack.objects.bulk_create(objs)
            finished_tracks.append(objs)

            next_page_token = tracks.get('nextPageToken')

            if not next_page_token:
                break

            params['pageToken'] = next_page_token

        return finished_tracks

    def create_playlists_selection(self):
        # TODO: need to write this part to give chose option for user to which playlists
        #  will be added.
        raise NotImplemented()

    def create_playlist(self, playlist_data: dict) -> dict:
        """
        Post a new playlists in user account. Max create playlist limit is set to
         10 per day.
        """
        params = {'part': self.part}

        request_data = {
            "snippet": {
                "title": playlist_data['playlist_name'],
                "description": playlist_data.get('description')
            },
            "status": {
                "privacyStatus": playlist_data.get('privacy_status')
            }
        }

        response = self.youtube_client.create_a_playlist(params, request_data)
        playlist_data = self.validate_response(response)

        created_playlist = {
            "name": playlist_data['snippet']['title'],
            "status": playlist_data['status']['privacyStatus'],
            "remote_id": playlist_data['id'],
            "provider": Provider.YOUTUBE,
            "user": self.user
        }
        CreatedPlaylist.objects.create(**created_playlist)

        return created_playlist

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

        response = self.youtube_client.add_tracks_to_playlist(
            params=params, request_data=request_data
        )
        self.validate_response(response)

        return response

    def search(self, search_track: str, search_type: str = None) -> dict:
        """
        Search for given tracks and append results to later use in add tracks to
        playlist.
        """
        params = {
            'part': 'snippet',
            'q': search_track,
        }

        response = self.youtube_client.search(params)
        search_result = self.validate_response(response)

        try:
            search_response = {
                'id': search_result['items'][0]['id']['videoId'],
                'name': search_result['items'][0]['snippet']['title'],
                'type': None,
            }
        except (KeyError, TypeError):
            self.create_search_error(
                search_track=search_track,
                search_result=search_result,
                user=self.user
            )
            raise ProviderResponseError(f"{search_track} not found.")

        return search_response
