from django.conf import settings
from rest_framework import status

from apps.auths.user.api.viewsets import LoginView, UserMePassView
from core.tests.base import APITestCase
from core.tests.factories import make_user
from utils.api.throttling import AuthAnonRateThrottle, PasswordChangeUserRateThrottle


class AuthAPITest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = make_user(username="authuser", email="auth@example.com")
        self.login_url = "/api/auth/token/"
        self.me_url = "/api/auth/me/"
        self.password_url = "/api/auth/me/reset_password/"

    def test_login_returns_tokens_and_user(self):
        response = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "auth@example.com")

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        self.authenticate(self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "auth@example.com")

    def test_password_change_success(self):
        self.authenticate(self.user)
        response = self.client.post(
            self.password_url,
            {
                "current_password": "SecurePass123!",
                "new_password": "NewSecurePass456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass456!"))

    def test_password_change_rejects_weak_password(self):
        self.authenticate(self.user)
        response = self.client.post(
            self.password_url,
            {
                "current_password": "SecurePass123!",
                "new_password": "123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_auth_views_use_rate_throttling(self):
        self.assertIn(AuthAnonRateThrottle, LoginView.throttle_classes)
        self.assertIn(PasswordChangeUserRateThrottle, UserMePassView.throttle_classes)
        self.assertIn("auth", settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"])

    def test_token_refresh_returns_new_access(self):
        login = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "SecurePass123!"},
            format="json",
        )
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": login.data["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_patch_updates_profile(self):
        self.authenticate(self.user)
        response = self.client.patch(
            self.me_url,
            {"phone": "987654321"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], "987654321")


class PermissionListAPITest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = make_user(username="permuser", email="perm@example.com")
        self.permissions_url = "/api/permissions/"

    def test_permissions_list_requires_authentication(self):
        response = self.client.get(self.permissions_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permissions_list_returns_business_permissions(self):
        self.authenticate(self.user)
        response = self.client.get(self.permissions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codenames = {item["codename"] for item in response.data}
        self.assertIn("add_user", codenames)
        self.assertNotIn("add_logentry", codenames)
