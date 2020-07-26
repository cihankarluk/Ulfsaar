from rest_framework import serializers

from musicwire.core.serializers import BaseSerializer


class TransferPlaylistSerializer(BaseSerializer, serializers.Serializer):
    from_ = serializers.CharField()
    from_token = serializers.CharField()
    to_ = serializers.CharField()
    to_token = serializers.CharField()
    user_id = serializers.CharField(required=False)
