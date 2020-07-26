from musicwire.provider.clients.base import BaseClient


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(**kwargs)
        self.token = kwargs['token']

    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        return headers

    def update_params(self, params):
        params['access_token'] = self.token
        return params

    def get_playlists(self, params: dict):
        end_point = "playlists"
        return self.make_request(end_point=end_point, params=params)

    def get_playlist_tracks(self, params: dict):
        end_point = "playlistItems"
        return self.make_request(end_point=end_point, params=params)

    def create_a_playlist(self, params: dict, request_data: dict):
        end_point = "playlists"
        return self.make_request(end_point=end_point, data=request_data, params=params,
                                 method="POST")

    def add_tracks_to_playlist(self, params: dict, request_data: dict):
        end_point = "playlistItems"
        return self.make_request(end_point=end_point, data=request_data, params=params,
                                 method="POST")

    def search(self, params: dict):
        end_point = "search"
        return self.make_request(end_point=end_point, params=params)
