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
                                    data=json.dumps(post_data), params=params)

    def get_playlists(self, params: dict) -> dict:
        end_point = "playlists"
        return self.make_request(end_point=end_point, params=params)

    def get_playlist_tracks(self, params: dict) -> dict:
        end_point = "playlistItems"
        return self.make_request(end_point=end_point, params=params)

    def create_a_playlist(self, params: dict, request_data: dict) -> dict:
        end_point = "playlists"
        return self.make_request(end_point=end_point, data=request_data, params=params,
                                 method="POST")

    def add_tracks_to_playlist(self, params: dict, request_data: dict) -> dict:
        end_point = "playlistItems"
        return self.make_request(end_point=end_point, data=request_data, params=params,
                                 method="POST")

    def search(self, params: dict) -> dict:
        end_point = "search"
        return self.make_request(end_point=end_point, params=params)
