import json

from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APIClient

from musicwire.account.models import UserProfile


class UserSignUpTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("sing_up")

    def test_user_sign_up_with_missing_field(self):
        request_data = {
            "username": "test",
            "email": "test@test.com"
        }

        expected_result = {
            'status_code': 400,
            'code': 'VALIDATION_ERROR',
            'error_message': {
                'password': ['This field is required.']
            }
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json"
        )

        self.assertEqual(expected_result, response.json())

    def test_user_sign_up_with_correctly(self):
        request_data = {
            "username": "test",
            "password": "test_pwd",
            "email": "test@test.com"
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json"
        )

        self.assertEqual(201, response.status_code)

    def test_user_sign_up_with_already_existing_username(self):
        mommy.make(UserProfile, username="test")
        request_data = {
            "username": "test",
            "password": "test_pwd",
            "email": "test@test.com"
        }

        expected_result = {
            'status_code': 400,
            'code': 'USERNAME_ALREADY_EXISTS',
            'error_message': 'Please try another username.'
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json"
        )

        self.assertEqual(expected_result, response.json())


class UserSignInTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("sign_in")

    def test_user_sign_in_with_wrong_username(self):
        mommy.make(UserProfile)
        request_data = {
            "username": "test_username",
            "password": "test_password"
        }

        expected_result = {
            'status_code': 400,
            'code': 'USER_SIGN_IN_ERROR',
            'error_message': 'Please control username or password.'
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json"
        )

        self.assertEqual(expected_result, response.json())

    def test_user_sign_in_success(self):
        mommy.make(UserProfile, username="test_username", password="test_password")
        request_data = {
            "username": "test_username",
            "password": "test_password"
        }

        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type="application/json"
        )

        self.assertEqual(200, response.status_code)
