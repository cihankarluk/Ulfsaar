from unittest import mock
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from musicwire.core.exceptions import ValidationError
from musicwire.provider.adapters.spotify import Adapter


class SpotifyAdapterTestCase(TestCase):
    def setUp(self) -> None:
        self.spotify_client = APIClient()
        self.adapter = Adapter(token='test')

    def test_collector_if_limit_over_50(self):
        """
        Expect validation error for too big limit parameter.
        """
        with self.assertRaises(ValidationError) as ve:
            self.adapter.collector(mock.MagicMock(), limit=100, offset=0)

        self.assertIsNotNone(ve)

    def test_collector_if_response_is_empty(self):
        """
        Expect to get None result from method.
        """
        fn = mock.MagicMock(return_value=None)

        response = self.adapter.collector(fn, limit=50, offset=0)

        self.assertListEqual(response, [])

    def test_collector_if_collect_concurrently_called(self):
        """
        Expect everything goes well and collect_concurrently called end of the program.
        """
        return_value = {'total': 20}
        fn = mock.MagicMock(return_value=return_value)
        fn.__name__ = 'test'

        with patch("musicwire.provider.adapters.spotify.Adapter.collect_concurrently") as cc:
            self.adapter.collector(fn, limit=50, offset=0)

        cc.assert_called()
        cc.assert_called_once_with(fn, [{'limit': 50, 'offset': 0}], 'test')

    def test_saved_tracks_if_no_tracks_returns(self):
        """
        Expect no result due to access token is wrong.
        """
        result = self.adapter.saved_tracks(50, 0)

        self.assertListEqual(result, [])

    def test_saved_tracks_if_track_exists(self):
        return_value = [
            {
                "items": [
                    {
                        "track": {
                            "id": "Test ID",
                            "album": {"name": "Test Album Name"},
                            "name": "Test Name",
                            "artists": [
                                {"name": "Test Artist Name"}
                            ],
                            "uri": "Test Uri"
                        }
                    }
                ]
            }
        ]
        expected_result = [
            {
                'track_id': return_value[0]['items'][0]['track']['id'],
                'track_album_name': return_value[0]['items'][0]['track']['album'][
                    'name'],
                'track_name': return_value[0]['items'][0]['track']['name'],
                'track_artist': return_value[0]['items'][0]['track']['artists'][0][
                    'name'],
                'track_uri': return_value[0]['items'][0]['track']['uri']
            }
        ]

        self.adapter.collector = mock.MagicMock(return_value=return_value)

        result = self.adapter.saved_tracks()

        self.assertEqual(result, expected_result)

    def test_playlists_if_no_playlist_returns(self):
        """
        Expect no result due to access token is wrong so client returns error.
        """
        result = self.adapter.playlists()

        self.assertListEqual(result, [])

    def test_playlists_if_playlist_exists(self):
        return_value = [
            {
                "items": [
                    {
                        "id": "Test Playlist ID",
                        "name": "Test Name",
                        "public": True,
                        "uri": "Test Uri"
                    }
                ]
            }
        ]

        expected_result = [
            {
                'playlist_id': return_value[0]['items'][0]['id'],
                'playlist_name': return_value[0]['items'][0]['name'],
                'playlist_public': return_value[0]['items'][0]['public'],
                'playlist_uri': return_value[0]['items'][0]['uri']
            }
        ]

        self.adapter.collector = mock.MagicMock(return_value=return_value)

        result = self.adapter.playlists()

        self.assertEqual(result, expected_result)

    def test_albums_if_no_album_returns(self):
        result = self.adapter.albums()

        self.assertListEqual(result, [])

    def test_albums_if_albums_exists(self):
        return_value = [
            {
                "items": [
                    {
                        "album": {
                            "id": "Test Album ID",
                            "name": "Test Name",
                            "popularity": 1,
                            "uri": "Test Uri"
                        }
                    }
                ]
            }
        ]

        expected_result = [
            {
                'album_id': return_value[0]['items'][0]["album"]['id'],
                'album_name': return_value[0]['items'][0]["album"]['name'],
                'album_popularity': return_value[0]['items'][0]["album"]['popularity'],
                'album_uri': return_value[0]['items'][0]["album"]['uri']
            }
        ]

        self.adapter.collector = mock.MagicMock(return_value=return_value)

        result = self.adapter.albums()

        self.assertEqual(result, expected_result)

    @patch("musicwire.provider.adapters.spotify.Adapter.get_saved_tracks")
    def test_playlist_tracks(self, get_saved_tracks):
        self.adapter.playlist_tracks("Test Id")

        get_saved_tracks.assert_called_once()

    def test_create_playlist_if_playlist_has_error(self):
        request_data = {
            'name': 'Test Name'
        }
        result = self.adapter.create_playlist("Test User ID", **request_data)

        self.assertIsNone(result)

    def test_create_playlist_if_playlist_created(self):
        client = self.adapter.spotify_client

        request_data = {
            'name': 'Test Name',
            'public': True,
            'collaborative': 'Test Collaborative',
            'description': 'Test Description'
        }

        client.create_a_playlist = mock.MagicMock()

        self.adapter.create_playlist("Test User ID", **request_data)

        client.create_a_playlist.assert_called_with("Test User ID", request_data)

    def test_add_tracks_to_playlist(self):
        ...

    def test_upload_playkist_cover_image(self):
        ...

    def test_search(self):
        ...