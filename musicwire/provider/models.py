from django.db import models

from musicwire.provider.helpers import import_provider_class


class Provider(models.Model):
    SPOTIFY = 'spotify'
    YOUTUBE = 'youtube'

    PROVIDERS = (
        (SPOTIFY, 'spotify'),
        (YOUTUBE, 'youtube')
    )

    name = models.CharField(max_length=64, choices=PROVIDERS)
    base_url = models.URLField()

    def __str__(self):
        return self.name

    @staticmethod
    def get_provider(provider: str, token: str, user: object):
        """
        Get interested Adapter.
        """
        provider_module = import_provider_class(provider)
        adapter = provider_module(token=token, user=user)
        return adapter
