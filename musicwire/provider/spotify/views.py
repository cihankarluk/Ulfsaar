from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from musicwire.provider.spotify.serializers import SpotifySerializer
from musicwire.provider.spotify.spotify_client import Client


class SavedTracksView(APIView):
    serializer_class = SpotifySerializer

    @staticmethod
    def get_client(token):
        req_data = {
            'base_url': "https://api.spotify.com/v1/",
            'token': token,
            'end_point': "me/tracks"
        }
        cls = Client(**req_data)
        return cls

    def get_tracks(self, tracks: list, cls: Client, limit=50, offset=0):
        params = {'limit': limit, 'offset': offset}
        response = cls.make_request(params=params)
        if not response:
            return
        data = response['items']
        for item in data:
            item = item['track']
            music_data = {
                'track_id': item['id'],
                'track_album_name': item['album']['name'],
                'track_name': item['name'],
                'track_artist': item['artists'][0]['name'],
                'track_uri': item['uri']
            }
            tracks.append(music_data)
        if response.get('next'):
            self.get_tracks(tracks=tracks, cls=cls, offset=offset+limit)

    def post(self, request, *args, **kwargs):
        tracks = []
        token = request.data['token']
        cls = self.get_client(token)
        self.get_tracks(tracks=tracks, cls=cls)
        paginator = Paginator(tracks, 25)
        result = paginator.page(1)
        return Response(result.object_list)

