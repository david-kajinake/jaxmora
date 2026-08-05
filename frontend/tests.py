from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('frontend:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jaxmora/home.html')
        self.assertContains(response, "Africa's home of")
        self.assertContains(response, 'frontend/css/home.css')


class AuthenticationPageTests(TestCase):
    def test_authentication_pages_render(self):
        for name in ('login', 'signup', 'password_reset'):
            response = self.client.get(reverse(f'frontend:{name}'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<form', html=False)

    def test_signup_creates_and_signs_in_a_user(self):
        response = self.client.post(
            reverse('frontend:signup'),
            {
                'username': 'cinema_fan',
                'email': 'fan@example.com',
                'password1': 'JaxmoraPass2026!',
                'password2': 'JaxmoraPass2026!',
            },
        )

        self.assertRedirects(response, reverse('frontend:home'))
        user = get_user_model().objects.get(username='cinema_fan')
        self.assertEqual(user.email, 'fan@example.com')
        self.assertEqual(str(self.client.session['_auth_user_id']), str(user.pk))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_a_reset_email_for_a_known_user(self):
        get_user_model().objects.create_user(
            username='reset_user',
            email='reset@example.com',
            password='JaxmoraPass2026!',
        )

        response = self.client.post(
            reverse('frontend:password_reset'),
            {'email': 'reset@example.com'},
        )

        self.assertRedirects(response, reverse('frontend:password_reset'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your JAXMORA password', mail.outbox[0].subject)
