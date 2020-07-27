from rest_framework import serializers

from musicwire.core.serializers import BaseSerializer
from musicwire.music.models import Playlist, PlaylistTrack


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ("name", "status", "remote_id", "content", "provider", "is_transferred")


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistTrack
        fields = ("name", "artist", "album", "remote_id", "is_transferred",
                  "provider")

    def to_representation(self, instance):
        data = super(TrackSerializer, self).to_representation(instance)
        data['playlist_name'] = instance.playlist.name
        return data


class PlaylistPostSerializer(BaseSerializer, serializers.Serializer):
    source = serializers.CharField()
    source_token = serializers.CharField()


class TrackPostSerializer(BaseSerializer, serializers.Serializer):
    source = serializers.CharField()
    source_token = serializers.CharField()
    playlist_id = serializers.CharField()
