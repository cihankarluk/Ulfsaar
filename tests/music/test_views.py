import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APIClient

from musicwire.account.models import UserProfile
from musicwire.music.models import Playlist, PlaylistTrack, CreatedPlaylist


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
            content=3,
            provider="test_provider",
            is_transferred=True
        )
        mommy.make(Playlist, user=self.user2)

        request_data = {
            "name": "test_name_1",
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

    def test_post_playlist_if_extra_parameter_in_request_data(self):
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


class PlaylistTrackViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("playlist_track")
        self.user1 = mommy.make(UserProfile, token='user1_token')
        self.user2 = mommy.make(UserProfile, token='user2_token')
        self.playlist1 = mommy.make(Playlist, user=self.user1, name="test_1")
        self.playlist2 = mommy.make(Playlist, user=self.user2, name="test_2")
        self.headers = {
            "Content-Type": "application/json",
            "HTTP_TOKEN": "user1_token"
        }

    def test_get_playlist_track_if_user_is_not_authenticated(self):
        expected_result = {
            'status_code': 401,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }

        response = self.client.get(self.url)

        self.assertEqual(expected_result, response.json())

    def test_get_playlist_track_if_user_is_authenticated(self):
        mommy.make(PlaylistTrack, playlist=self.playlist1, user=self.user1)
        mommy.make(PlaylistTrack, playlist=self.playlist2, user=self.user2)

        response = self.client.get(
            self.url,
            **self.headers
        )

        self.assertEqual(1, response.json()['count'])

    def test_get_playlist_track_if_filter_tracks(self):
        mommy.make(
            PlaylistTrack,
            user=self.user1,
            name="test_name_1",
            artist="test_artist",
            album="test_album",
            playlist=self.playlist1,
            remote_id="test_remote_id_1",
            is_transferred=True,
            provider="test_provider",
        )
        mommy.make(
            PlaylistTrack,
            user=self.user1,
            name="test_name_2",
            artist="test_artist",
            album="test_album",
            playlist=self.playlist1,
            remote_id="test_remote_id_2",
            is_transferred=False,
            provider="test_provider",
        )

        request_data = {
            "name": "test_name_1",
            "artist": "test_artist",
            "album": "test_album",
            "playlist_name": "test_1",
            "remote_id": "test_remote_id_1",
            "is_transferred": True,
            "provider": "test_provider"
        }

        response = self.client.get(
            self.url,
            **self.headers,
            data=request_data
        )

        expected_result = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{'name': 'test_name_1',
                         'artist': 'test_artist',
                         'album': 'test_album',
                         'remote_id': 'test_remote_id_1',
                         'is_transferred': True,
                         'provider': 'test_provider',
                         'playlist_name': 'test_1'}]
        }

        self.assertEqual(expected_result, response.json())

    def test_post_playlist_tracks_if_user_is_not_authenticated(self):
        expected_result = {
            'status_code': 401,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }

        response = self.client.post(self.url)

        self.assertEqual(expected_result, response.json())

    def test_post_playlist_track_if_extra_parameter_in_request_data(self):
        request_data = {
            "source": "spotify",
            "source_token": "test_token",
            "playlist_id": "test_playlist_id",
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

    def test_post_playlist_track_if_user_is_authenticated(self):
        track = mommy.make(
            PlaylistTrack,
            user=self.user1,
            name="Six Minutes",
            artist="Snoop Dog",
            album="test_album",
            playlist=self.playlist1,
            remote_id="test_remote_id",
            is_transferred=False,
            provider="spotify",
        )

        request_data = {
            "source": "spotify",
            "source_token": "test_token",
            "playlist_id": "spotify_saved_tracks"
        }

        expected_result = [{
            'name': 'Six Minutes',
            'artist': 'Snoop Dog',
            'album': 'test_album',
            'remote_id': 'test_remote_id',
            'is_transferred': False,
            'provider': 'spotify',
            'playlist_name': 'test_1'
        }]

        patch_address = "musicwire.provider.adapters.spotify.Adapter.saved_tracks"
        return_value = [[track], []]

        with patch(patch_address, return_value=return_value):
            response = self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type="application/json",
                **self.headers
            )

        self.assertEqual(expected_result, response.json())

    def test_post_playlist_track_if_all_tracks_already_processed(self):
        request_data = {
            "source": "spotify",
            "source_token": "test_token",
            "playlist_id": "spotify_saved_tracks"
        }

        expected_result = {
            'status_code': 400,
            'code': 'ALL_TRACKS_ALREADY_PROCESSED',
            'error_message': 'All tracks on this playlist already processed.'
        }

        patch_address = "musicwire.provider.adapters.spotify.Adapter.saved_tracks"
        return_value = [[], []]

        with patch(patch_address, return_value=return_value):
            response = self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type="application/json",
                **self.headers
            )

        self.assertEqual(expected_result, response.json())


class CreatePlaylistViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("create_playlist")
        self.user1 = mommy.make(UserProfile, token='user1_token')
        self.user2 = mommy.make(UserProfile, token='user2_token')
        self.headers = {
            "Content-Type": "application/json",
            "HTTP_TOKEN": "user1_token"
        }

    def test_get_created_playlist_if_user_is_not_authenticated(self):
        expected_result = {
            'status_code': 401,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }

        response = self.client.get(self.url)

        self.assertEqual(expected_result, response.json())

    def test_get_created_playlist_if_user_is_authenticated(self):
        mommy.make(CreatedPlaylist, user=self.user1)
        mommy.make(CreatedPlaylist, user=self.user2)

        response = self.client.get(
            self.url,
            **self.headers
        )

        self.assertEqual(1, response.json()['count'])

    def test_get_created_playlist_if_filter_playlists(self):
        mommy.make(
            CreatedPlaylist,
            user=self.user1,
            name="test_name_1",
            status="test_status",
            remote_id="test_remote_id_1",
            provider="test_provider",
        )
        mommy.make(
            CreatedPlaylist,
            user=self.user1,
            name="test_name_2",
            status="test_status",
            remote_id="test_remote_id_2",
            provider="test_provider",
        )

        request_data = {
            "name": "test_name_1",
            "status": "test_status",
            "playlist_id": "test_remote_id_1",
            "provider": "test_provider"
        }

        response = self.client.get(
            self.url,
            **self.headers,
            data=request_data
        )

        expected_result = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{'name': 'test_name_1',
                         'status': 'test_status',
                         'remote_id': 'test_remote_id_1',
                         'provider': 'test_provider'}]
        }

        self.assertEqual(expected_result, response.json())

    def test_post_create_playlist_if_user_is_not_authenticated(self):
        expected_result = {
            'status_code': 401,
            'code': 'AUTHENTICATION_FAIL',
            'error_message': 'Authentication Failed'
        }

        response = self.client.post(self.url)

        self.assertEqual(expected_result, response.json())

    def test_post_create_playlist_if_extra_parameter_in_request_data(self):
        request_data = {
            "end": "youtube",
            "end_token": "test_token",
            "playlist_name": "test_playlist_name",
            "privacy_status": "test_privacy_status",
            "collaborative": "test_collaborative",
            "description": "test_description",
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

    def test_post_create_playlist_if_end_is_spotify(self):
        """
        If end is spotify user id is required.
        """
        request_data = {
            "end": "spotify",
            "end_token": "test_token",
            "playlist_name": "test_playlist_name",
            "privacy_status": "test_privacy_status",
            "collaborative": "test_collaborative",
            "description": "test_description",
        }

        expected_result = {
            'status_code': 400,
            'code': 'VALIDATION_ERROR',
            'error_message': {'end': ['user_id is required for Spotify.']}
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json",
            **self.headers
        )

        self.assertEqual(expected_result, response.json())

    def test_post_create_playlist_if_user_is_authenticated(self):
        request_data = {
            "end": "spotify",
            "end_token": "test_token",
            "playlist_name": "test_playlist_name",
            "privacy_status": "test_privacy_status",
            "collaborative": "test_collaborative",
            "description": "test_description",
            "user_id": "test_user_id"
        }

        patch_address = "musicwire.provider.adapters.spotify.Adapter.create_playlist"
        return_value = []

        with patch(patch_address, return_value=return_value) as p:
            self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type="application/json",
                **self.headers
            )

        p.assert_called_with(request_data)
