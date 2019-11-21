from rest_framework import serializers


class SpotifySerializer(serializers.Serializer):
    token = serializers.CharField()
    end_point = serializers.CharField()
