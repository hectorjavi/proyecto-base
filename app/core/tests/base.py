from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@override_settings(DEBUG=False)
class APITestCase(TestCase):
    """Base API tests without dev-only post_migrate superuser seeding."""

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, user):
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    def clear_credentials(self):
        self.client.credentials()
