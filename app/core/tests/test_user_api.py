from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from apps.models.user.models import User
from core.tests.base import APITestCase
from core.tests.factories import make_user


class UserAPITest(APITestCase):
    def setUp(self):
        super().setUp()
        self.list_url = "/api/users/"
        self.admin = make_user(
            username="adminuser",
            email="admin@example.com",
            is_staff=True,
            is_superuser=True,
        )
        self.regular = make_user(
            username="regularuser",
            email="regular@example.com",
        )

    def test_list_users_requires_view_permission(self):
        self.authenticate(self.regular)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_list_users(self):
        self.authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 2)

    def test_create_user_rejects_weak_password(self):
        self.authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            {
                "username": "newbie",
                "password": "123",
                "first_name": "New",
                "paternal_last_name": "User",
                "maternal_last_name": "Test",
                "email": "newbie@example.com",
                "gender": User.MALE,
                "accepted_terms": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_create_user_with_valid_password(self):
        self.authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            {
                "username": "newbie2",
                "password": "ValidPass123!",
                "first_name": "New",
                "paternal_last_name": "User",
                "maternal_last_name": "Test",
                "email": "newbie2@example.com",
                "gender": User.MALE,
                "accepted_terms": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(email="newbie2@example.com")
        self.assertTrue(created.check_password("ValidPass123!"))

    def test_user_with_view_permission_can_list(self):
        content_type = ContentType.objects.get_for_model(User)
        view_perm = Permission.objects.get(
            codename="view_user",
            content_type=content_type,
        )
        self.regular.user_permissions.add(view_perm)
        self.authenticate(self.regular)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_exposes_gender_code_and_display(self):
        self.authenticate(self.admin)
        response = self.client.get(f"{self.list_url}{self.admin.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["gender"], User.MALE)
        self.assertEqual(response.data["gender_display"], "Masculino")
