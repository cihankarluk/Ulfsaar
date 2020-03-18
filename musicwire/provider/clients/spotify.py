import json
import urllib.parse

import requests

from musicwire.core.helpers import request_validator


class Client:
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs['base_url']
        self.token = kwargs['token']

    @request_validator
    def make_request(self, end_point, params=None, data=None, method='GET'):
        url = urllib.parse.urljoin(self.base_url, end_point)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        if method.lower() in ('get', 'delete'):
            return requests.request(method, url=url, headers=headers, params=params)
        else:
            # Two repeated code due to differentiate post and get methods.
            post_data = dict([(k, v) for k, v in data.items() if v is not None])
            return requests.request(method, url=url, headers=headers,
                                    data=json.dumps(post_data))

    def get_saved_tracks(self, request_data):
        end_point = "me/tracks"
        return self.make_request(end_point=end_point, params=request_data)

    def get_playlists(self, request_data):
        end_point = "me/playlists"
        return self.make_request(end_point=end_point, params=request_data)

    def get_albums(self, request_data):
        end_point = "me/albums"
        return self.make_request(end_point=end_point, params=request_data)

    def get_playlist_tracks(self, request_data):
        # Bad practice to change data with pop.
        playlist_id = request_data.pop('playlist_id')
        end_point = f"playlists/{playlist_id}/tracks"
        return self.make_request(end_point=end_point, params=request_data)

    def create_a_playlist(self, user_id, request_data):
        end_point = f"users/{user_id}/playlists"
        return self.make_request(end_point=end_point, data=request_data, method='POST')

    def add_tracks_to_playlist(self, playlist_id, request_data):
        end_point = f"playlists/{playlist_id}/tracks"
        return self.make_request(end_point=end_point, data=request_data, method='POST')

    def upload_playlist_cover_image(self):
        # TODO: Later can be implemented.
        raise NotImplemented()

    def search(self, request_data):
        end_point = "search"
        return self.make_request(end_point=end_point, params=request_data)
