from rest_framework import serializers


class SpotifySerializer(serializers.Serializer):
    token = serializers.CharField()
