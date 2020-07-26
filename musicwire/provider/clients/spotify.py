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

    def search(self, params):
        end_point = "search"
        return self.make_request(end_point=end_point, params=params)
