from rest_framework import serializers

from musicwire.core.serializers import BaseSerializer


class PlaylistsSerializer(BaseSerializer, serializers.Serializer):
    source = serializers.CharField()
    source_token = serializers.CharField()


class TracksSerializer(BaseSerializer, serializers.Serializer):
    source = serializers.CharField()
    source_token = serializers.CharField()
    playlist_id = serializers.CharField()
