from rest_framework import serializers

from musicwire.core.exceptions import ValidationError
from musicwire.core.serializers import BaseSerializer
from musicwire.music.models import CreatedPlaylist, Playlist, PlaylistTrack, \
    SearchErrorTrack
from musicwire.provider.models import Provider


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = "name", "status", "remote_id", "content", "provider", "is_transferred"


class PulledPlaylistSerializer(serializers.Serializer):
    playlists = PlaylistSerializer(many=True)


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistTrack
        fields = "name", "artist", "album", "remote_id", "is_transferred", "provider"

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


class CreatePlaylistSerializer(BaseSerializer, serializers.Serializer):
    end = serializers.CharField()
    end_token = serializers.CharField()
    playlist_name = serializers.CharField()
    privacy_status = serializers.CharField(required=False)
    collaborative = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    user_id = serializers.CharField(required=False)

    def validate_end(self, val):
        user_id = self.initial_data.get('user_id')
        if val == Provider.SPOTIFY and user_id is None:
            raise ValidationError('user_id is required for Spotify.')
        return val


class CreatedPlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatedPlaylist
        fields = "name", "status", "remote_id", "provider"


class CreatedPlaylistDataSerializer(BaseSerializer, serializers.Serializer):
    name = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    playlist_id = serializers.CharField(required=False)
    provider = serializers.CharField(required=False)


class AddPlaylistTrackSerializer(BaseSerializer, serializers.Serializer):
    end = serializers.CharField()
    end_token = serializers.CharField()
    playlist_id = serializers.CharField()
    track_id = serializers.CharField()


class SearchSerializer(BaseSerializer, serializers.Serializer):
    source = serializers.CharField()
    source_token = serializers.CharField()
    track_name = serializers.CharField()


class SearchErrorSerializer(BaseSerializer, serializers.ModelSerializer):
    class Meta:
        model = SearchErrorTrack
        fields = '__all__'


class PlaylistTrackFilterSerializer(BaseSerializer, serializers.Serializer):
    name = serializers.CharField(required=False)
    artist = serializers.CharField(required=False)
    album = serializers.CharField(required=False)
    playlist_id = serializers.CharField(required=False)
    remote_id = serializers.CharField(required=False)
    is_transferred = serializers.BooleanField(required=False)
    provider = serializers.CharField(required=False)
    playlist_name = serializers.CharField(required=False)


class PlaylistFilterSerializer(BaseSerializer, serializers.Serializer):
    name = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    remote_id = serializers.CharField(required=False)
    content = serializers.IntegerField(required=False)
    provider = serializers.CharField(required=False)
    is_transferred = serializers.CharField(required=False)
