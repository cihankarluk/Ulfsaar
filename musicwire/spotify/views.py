from rest_framework.views import APIView

from musicwire.spotify.serializers import SpotifySerializer
from musicwire.spotify.spotify_client import Client


class SavedTracksView(APIView):
    serializer_class = SpotifySerializer

    def post(self, request, *args, **kwargs):
        saved_tracks = []
        req_data = {
            'base_url': "https://api.spotify.com/v1/me/tracks",
            'token': "BQDqTCTgnlj1i12rejGvpWt4N20TS-uIUsFYPzT9tXbznyMxeRooqlujqWd4vwKjxg-IpoUkOjjq4LbE-xl3fs2NAblaJ3bD3Xg_FP1-DHSpYq0M9gKkGd_cxkCu-jXtLL57I9zl2Q6sn18eMFC5XLvQG6yZUVv4c4pPoJqt2tAit_lca7TQw0zCNC79W9yASYxKjCUfaJ7GapKMVKIAOhR_JdvmTjC_ePEcS13X-JfkGULVKyhVEulOjCaqsDum-lox",

        }
        base_url = "https://api.spotify.com/v1/me/tracks"

        cls = Client(**req_data)
        response = cls.make_request()
        import ipdb;ipdb.set_trace()
