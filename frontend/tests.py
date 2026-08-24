import tempfile

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from api.models import Comedy, Movie, MovieLike, MovieView, UserPreferences


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
                'first_name': 'Cinema',
                'other_name': 'Fan',
                'email_address': 'fan@example.com',
                'phone_number': '+250788000000',
                'country': 'Rwanda',
                'password1': 'JaxmoraPass2026!',
                'password2': 'JaxmoraPass2026!',
            },
        )

        self.assertRedirects(response, reverse('frontend:home'))
        user = get_user_model().objects.get(username='cinema_fan')
        self.assertEqual(user.email_address, 'fan@example.com')
        self.assertEqual(user.phone_number, '+250788000000')
        self.assertEqual(str(self.client.session['_auth_user_id']), str(user.pk))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_a_reset_email_for_a_known_user(self):
        get_user_model().objects.create_user(
            username='reset_user',
            email='reset@example.com',
            password='JaxmoraPass2026!',
            first_name='Reset',
            other_name='User',
            email_address='reset@example.com',
            phone_number='+250788000001',
        )

        response = self.client.post(
            reverse('frontend:password_reset'),
            {'email': 'reset@example.com'},
        )

        self.assertRedirects(response, reverse('frontend:password_reset'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your JAXMORA password', mail.outbox[0].subject)


class DashboardUploadChooserTests(TestCase):
    def test_dashboard_renders_one_selectable_form_per_content_type(self):
        response = self.client.get(reverse('frontend:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-upload-type-picker')
        for content_type in ('movie', 'music', 'visual', 'comedy', 'serie'):
            self.assertContains(
                response,
                f'data-upload-type-control aria-controls="upload-form-{content_type}"',
            )
            self.assertContains(
                response, f'data-upload-form-panel="{content_type}"'
            )
        self.assertContains(response, 'id="upload-form-movie"')
        self.assertContains(response, 'id="upload-form-music"')
        self.assertContains(response, 'id="upload-form-visual"')
        self.assertContains(response, 'id="upload-form-comedy"')
        self.assertContains(response, 'id="upload-form-serie"')


class ProfileFormChooserTests(TestCase):
    def test_profile_renders_clickable_references_for_each_form(self):
        response = self.client.get(reverse('frontend:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-profile-form-picker')
        for form_type in ('details', 'password', 'delete'):
            self.assertContains(
                response, f'data-profile-form-target="{form_type}"'
            )
            self.assertContains(
                response, f'data-profile-form-panel="{form_type}"'
            )
        self.assertContains(response, 'id="profile-details-panel"')
        self.assertContains(response, 'id="profile-password-panel"')
        self.assertContains(response, 'id="profile-delete-panel"')


class CataloguePageTests(TestCase):
    def test_catalogue_pages_render_with_their_loader(self):
        expected_pages = {
            'films': 'films',
            'music': 'music',
            'comedy': 'comedy',
            'image_visuals': 'visuals',
        }

        for route_name, page_name in expected_pages.items():
            response = self.client.get(reverse(f'frontend:{route_name}'))

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f'data-catalog-page="{page_name}"')
            self.assertContains(response, 'id="load-more"')
            self.assertContains(response, 'frontend/js/catalog.js')


class CreatorDirectoryTests(TestCase):
    def test_creator_directory_contains_only_requested_categories(self):
        response = self.client.get(reverse('frontend:creators'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jaxmora/creators.html')
        self.assertContains(response, 'id="creator-search"')
        self.assertContains(response, 'data-creator-filter="movies"')
        self.assertContains(response, 'data-creator-filter="comedy"')
        self.assertContains(response, 'data-creator-filter="visual-images"')
        self.assertNotContains(response, 'Music creator')


class CustomUserAdminTests(TestCase):
    def test_custom_user_change_page_allows_non_editable_date_joined(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='JaxmoraPass2026!',
            first_name='Admin',
            other_name='User',
            email_address='admin@example.com',
            phone_number='+250788000010',
        )
        profile_user = user_model.objects.create_user(
            username='profile_user',
            email='profile@example.com',
            password='JaxmoraPass2026!',
            first_name='Profile',
            other_name='User',
            email_address='profile@example.com',
            phone_number='+250788000011',
        )

        self.client.force_login(admin_user)
        response = self.client.get(
            reverse('admin:api_user_change', args=(str(profile_user.pk),))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Date joined')


class AccountPageTests(TestCase):
    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.media_override.enable()
        self.user = get_user_model().objects.create_user(
            username='creator',
            email='creator@example.com',
            password='JaxmoraPass2026!',
            first_name='Creative',
            other_name='Person',
            email_address='creator@example.com',
            phone_number='+250788000012',
        )
        self.client.force_login(self.user)

    def tearDown(self):
        self.media_override.disable()
        self.temp_media.cleanup()
        super().tearDown()

    def test_authenticated_headers_include_the_account_dropdown(self):
        response = self.client.get(reverse('frontend:home'))

        self.assertContains(response, 'data-account-menu')
        for label in ('Dashboard', 'Profile', 'Settings', 'Privacy policy', 'Terms of service', 'Logout'):
            self.assertContains(response, label)

    def test_dashboard_shows_analytics_and_accepts_a_comedy_upload(self):
        movie = Movie.objects.create(
            owner=self.user,
            title='Analytics film',
            description='A film used for dashboard analytics tests.',
            price='1500.00',
            video=SimpleUploadedFile('analytics.mp4', b'video-content'),
            year_released=2026,
            category='Drama',
        )
        MovieView.objects.create(movie=movie, viewer=self.user)
        MovieLike.objects.create(movie=movie, liker=self.user)

        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.context['total_views'], 1)
        self.assertEqual(response.context['total_likes'], 1)

        response = self.client.post(
            reverse('frontend:dashboard'),
            {
                'content_type': 'comedy',
                'title': 'New comedy',
                'description': 'A brand new comedy for upload testing.',
                'price': '2000.00',
                'content_file': SimpleUploadedFile('new-comedy.mp4', b'video-content'),
                'year_released': 2026,
                'category': '',
                'trailer_link': '',
                'production_studio': '',
            },
        )

        self.assertRedirects(response, reverse('frontend:dashboard'))
        self.assertTrue(Comedy.objects.filter(owner=self.user, title='New comedy').exists())

    def test_profile_and_display_settings_are_saved(self):
        response = self.client.post(
            reverse('frontend:profile'),
            {
                'action': 'profile',
                'username': 'creator_renamed',
                'first_name': 'Updated',
                'other_name': 'Creator',
                'phone_number': '+250788000013',
                'email_address': 'updated@example.com',
            },
        )
        self.assertRedirects(response, reverse('frontend:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'creator_renamed')
        self.assertEqual(self.user.email, 'updated@example.com')

        response = self.client.post(
            reverse('frontend:settings'),
            {'language': 'rw', 'font_size': 'large', 'font_family': 'georgia'},
        )
        self.assertRedirects(response, reverse('frontend:settings'))
        preferences = UserPreferences.objects.get(user=self.user)
        self.assertEqual(preferences.language, 'rw')
        self.assertEqual(preferences.font_size, 'large')
        self.assertEqual(preferences.font_family, 'georgia')
