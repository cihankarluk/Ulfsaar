import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APIClient

from musicwire.account.models import UserProfile
from musicwire.music.models import Playlist


class PlaylistViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("playlist")
        self.user1 = mommy.make(UserProfile, token='user1_token')
        self.user2 = mommy.make(UserProfile, token='user2_token')
        self.headers = {
            "Content-Type": "application/json",
            "HTTP_TOKEN": "user1_token"
        }

    def test_get_playlists_if_user_is_not_authenticated(self):
        expected_result = {
            'status_code': 401,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }

        response = self.client.get(self.url)

        self.assertEqual(expected_result, response.json())

    def test_get_playlists_if_user_is_authenticated(self):
        mommy.make(Playlist, user=self.user1)
        mommy.make(Playlist, user=self.user2)

        response = self.client.get(
            self.url,
            **self.headers
        )

        self.assertEqual(1, response.json()['count'])

    def test_get_playlists_if_filter_playlists(self):
        mommy.make(
            Playlist,
            user=self.user1,
            name="test_name_1",
            status="test_public",
            remote_id="test_remote_id",
            content=2,
            provider="test_provider",
            is_transferred=False
        )
        mommy.make(
            Playlist,
            user=self.user1,
            name="test_name_2",
            status="test_public",
            remote_id="test_remote_id",
            content=2,
            provider="test_provider",
            is_transferred=True
        )
        mommy.make(Playlist, user=self.user2)

        request_data = {
            "name": "test_name",
            "status": "test_public",
            "remote_id": "test_remote_id",
            "content": 2,
            "provider": "test_provider",
            "is_transferred": False
        }

        expected_result = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{'name': 'test_name_1',
                         'status': 'test_public',
                         'remote_id': 'test_remote_id',
                         'content': '2',
                         'provider': 'test_provider',
                         'is_transferred': False}]
        }

        response = self.client.get(
            self.url,
            **self.headers,
            data=request_data
        )

        self.assertEqual(expected_result, response.json())

    def test_post_playlists_if_user_is_not_authenticated(self):
        expected_result = {
            'status_code': 401,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }

        response = self.client.post(self.url)

        self.assertEqual(expected_result, response.json())

    @patch("musicwire.provider.adapters.spotify.Adapter.playlists", return_value=[])
    def test_post_playlist_if_extra_parameter_in_request_data(self, _):
        request_data = {
            "source": "spotify",
            "source_token": "test_token",
            "test_parameter": "test_parameter"
        }

        expected_result = {
            'status_code': 400,
            'code': 'VALIDATION_ERROR',
            'error_message': {
                'non_field_errors': ["Got unknown fields: {'test_parameter'}"]
            }
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json",
            **self.headers
        )

        self.assertEqual(expected_result, response.json())

    @patch("musicwire.provider.adapters.spotify.Adapter.playlists", return_value=[])
    def test_post_playlists_if_user_is_authenticated(self, _):
        request_data = {
            "source": "spotify",
            "source_token": "test_token"
        }

        expected_result = {'playlists': [
            {'name': 'saved_tracks',
             'status': 'private',
             'remote_id': 'spotify_saved_tracks',
             'content': None,
             'provider': 'spotify',
             'is_transferred': False}]
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json",
            **self.headers
        )

        self.assertEqual(expected_result, response.json())
