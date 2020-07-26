from rest_framework import serializers

from musicwire.core.serializers import BaseSerializer


class UserCreateSerializer(BaseSerializer, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField(required=False)


class UserSignInSerializer(BaseSerializer, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
