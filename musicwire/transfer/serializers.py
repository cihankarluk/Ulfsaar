from rest_framework import serializers

from musicwire.core.exceptions import ValidationError


class TransferPlaylistSerializer(serializers.Serializer):
    from_ = serializers.CharField()
    from_token = serializers.CharField()
    to_ = serializers.CharField()
    to_token = serializers.CharField()
    user_id = serializers.CharField(required=False)

    def validate(self, attrs):
        initial_data_keys = self.initial_data.keys()
        unknown_keys = set(initial_data_keys) - set(self.fields.keys())
        if unknown_keys:
            raise ValidationError(f"Got unknown fields: {unknown_keys}")
        return attrs
