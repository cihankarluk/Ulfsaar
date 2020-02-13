from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from musicwire.provider.spotify.serializers import SpotifySerializer


class SavedTracksView(APIView):
    serializer_class = SpotifySerializer

    def post(self, request, *args, **kwargs):
        tracks = []
        token = request.data['token']
        paginator = Paginator(tracks, 25)
        result = paginator.page(1)
        return Response(result.object_list)

