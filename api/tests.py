from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class CurrentUserAPITests(APITestCase):
    def setUp(self):
        self.password = 'JaxmoraPass2026!'
        self.user = get_user_model().objects.create_user(
            username='signed_in_user',
            password=self.password,
            first_name='Signed',
            other_name='In',
            email='signed-in@example.com',
            email_address='signed-in@example.com',
            phone_number='+250788000099',
        )

    def test_current_user_is_available_after_token_login(self):
        """The frontend relies on this request immediately after sign-in."""
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': self.user.username, 'password': self.password},
            format='json',
        )

        self.assertEqual(token_response.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )
        response = self.client.get(reverse('current_user'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)

    def test_current_user_requires_authentication(self):
        response = self.client.get(reverse('current_user'))

        self.assertEqual(response.status_code, 401)
