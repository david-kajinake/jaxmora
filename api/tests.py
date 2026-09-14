from base64 import b64decode
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import (
    Comedy,
    Episode,
    EpisodeView,
    Movie,
    MovieComment,
    MovieLike,
    MovieView,
    Music,
    Season,
    Serie,
    VisualImage,
)


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


class PublicContentAPITests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username='film_creator',
            password='JaxmoraPass2026!',
            first_name='Film',
            other_name='Creator',
            email='creator@example.com',
            email_address='creator@example.com',
            phone_number='+250788000101',
            country='Rwanda',
        )
        self.viewer = get_user_model().objects.create_user(
            username='viewer',
            password='JaxmoraPass2026!',
            first_name='Active',
            other_name='Viewer',
            email='viewer@example.com',
            email_address='viewer@example.com',
            phone_number='+250788000102',
            country='Kenya',
        )
        self.same_country_owner = get_user_model().objects.create_user(
            username='same_country_creator',
            password='JaxmoraPass2026!',
            first_name='Same',
            other_name='Country',
            email='same-country@example.com',
            email_address='same-country@example.com',
            phone_number='+250788000103',
            country='Rwanda',
        )
        self.movie = Movie.objects.create(
            owner=self.owner,
            title='API-backed film',
            description='A real film returned by the API.',
            price='2000.00',
            video=SimpleUploadedFile('film.mp4', b'video-content'),
            year_released=2026,
            category='Drama',
            production_studio='JAXMORA Studios',
        )
        self.related_movie = Movie.objects.create(
            owner=self.owner,
            title='Related API-backed film',
            description='Another real film returned by the API.',
            price='2500.00',
            video=SimpleUploadedFile('related.mp4', b'video-content'),
            year_released=2026,
            category='Drama',
            production_studio='Another studio',
        )
        self.studio_related_movie = Movie.objects.create(
            owner=self.owner,
            title='Studio-related film',
            description='A film from the same production studio.',
            price='1800.00',
            video=SimpleUploadedFile('studio.mp4', b'video-content'),
            year_released=2025,
            category='Action',
            production_studio='JAXMORA Studios',
        )
        self.unrelated_movie = Movie.objects.create(
            owner=self.owner,
            title='Unrelated film',
            description='A film with a different category and studio.',
            price='1200.00',
            video=SimpleUploadedFile('unrelated.mp4', b'video-content'),
            year_released=2024,
            category='Comedy',
            production_studio='Other House',
        )
        self.music = Music.objects.create(
            owner=self.owner,
            title='API-backed track',
            description='A music video returned by the API.',
            price='500.00',
            video=SimpleUploadedFile('track.mp4', b'video-content'),
            year_released=2026,
            category='Afrobeat',
        )
        self.related_music = Music.objects.create(
            owner=self.owner,
            title='Related track',
            description='Another track in the same category.',
            price='500.00',
            video=SimpleUploadedFile('related-track.mp4', b'video-content'),
            year_released=2026,
            category='Afrobeat',
        )
        self.unrelated_music = Music.objects.create(
            owner=self.owner,
            title='Unrelated track',
            description='A track in a different category.',
            price='500.00',
            video=SimpleUploadedFile('unrelated-track.mp4', b'video-content'),
            year_released=2025,
            category='Jazz',
        )
        self.comedy = Comedy.objects.create(
            owner=self.owner,
            title='API-backed comedy',
            description='A comedy returned by the API.',
            price='500.00',
            video=SimpleUploadedFile('comedy.mp4', b'video-content'),
            year_released=2026,
        )
        self.owner_related_comedy = Comedy.objects.create(
            owner=self.owner,
            title='Same uploader comedy',
            description='Another comedy from the same creator.',
            price='500.00',
            video=SimpleUploadedFile('owner-comedy.mp4', b'video-content'),
            year_released=2026,
        )
        self.country_related_comedy = Comedy.objects.create(
            owner=self.same_country_owner,
            title='Same country comedy',
            description='A comedy from the same country.',
            price='500.00',
            video=SimpleUploadedFile('country-comedy.mp4', b'video-content'),
            year_released=2026,
        )
        self.unrelated_comedy = Comedy.objects.create(
            owner=self.viewer,
            title='Other country comedy',
            description='A comedy from another country.',
            price='500.00',
            video=SimpleUploadedFile('other-comedy.mp4', b'video-content'),
            year_released=2026,
        )
        self.visual = VisualImage.objects.create(
            owner=self.owner,
            title='API-backed visual',
            description='A visual image returned by the API.',
            price='500.00',
            image=SimpleUploadedFile('visual.jpg', b'image-content'),
            year_released=2026,
            category='Portrait',
        )
        self.related_visual = VisualImage.objects.create(
            owner=self.same_country_owner,
            title='Related visual',
            description='Another visual in the same category.',
            price='500.00',
            image=SimpleUploadedFile('related-visual.jpg', b'image-content'),
            year_released=2026,
            category='Portrait',
        )
        self.unrelated_visual = VisualImage.objects.create(
            owner=self.owner,
            title='Different category visual',
            description='A visual from the same uploader but another category.',
            price='500.00',
            image=SimpleUploadedFile('other-visual.jpg', b'image-content'),
            year_released=2026,
            category='Travel',
        )
        self.serie = Serie.objects.create(
            owner=self.owner,
            title='API-backed serie',
            description='A series with a real episode.',
            price='3000.00',
            year_released=2026,
            category='Drama',
        )
        self.season = Season.objects.create(
            serie=self.serie,
            ref_number=1,
            name='First season',
            year_released=2026,
        )
        self.episode = Episode.objects.create(
            season=self.season,
            name='First episode',
            ref_number=1,
            video=SimpleUploadedFile('episode.mp4', b'video-content'),
        )

    def test_movie_detail_exposes_display_name_related_content_and_unique_views(self):
        detail = self.client.get(reverse('movies-detail', args=(self.movie.pk,)))

        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['owner']['display_name'], 'Film Creator')
        self.assertEqual(detail.data['view_count'], 0)

        related = self.client.get(reverse('movies-related', args=(self.movie.pk,)))
        self.assertEqual(related.status_code, 200)
        self.assertEqual(
            {item['id'] for item in related.data},
            {str(self.related_movie.pk), str(self.studio_related_movie.pk)},
        )

        self.client.force_authenticate(self.viewer)
        view_response = self.client.post(reverse('movies-record-view', args=(self.movie.pk,)))
        second_view_response = self.client.post(
            reverse('movies-record-view', args=(self.movie.pk,))
        )

        self.assertEqual(view_response.data['view_count'], 1)
        self.assertEqual(second_view_response.data['view_count'], 1)

    def test_related_music_matches_the_same_category_only(self):
        related = self.client.get(reverse('music-related', args=(self.music.pk,)))

        self.assertEqual(related.status_code, 200)
        self.assertEqual([item['id'] for item in related.data], [self.related_music.pk])

    def test_related_comedy_matches_the_same_uploader_or_country(self):
        related = self.client.get(reverse('comedies-related', args=(self.comedy.pk,)))

        self.assertEqual(related.status_code, 200)
        self.assertEqual(
            {item['id'] for item in related.data},
            {str(self.owner_related_comedy.pk), str(self.country_related_comedy.pk)},
        )

    def test_related_visuals_match_the_same_category_only(self):
        for number in range(9):
            VisualImage.objects.create(
                owner=self.owner,
                title=f'Additional portrait {number}',
                description='Another visual in the same category.',
                price='500.00',
                image=SimpleUploadedFile(f'portrait-{number}.jpg', b'image-content'),
                year_released=2026,
                category='Portrait',
            )
        related = self.client.get(reverse('visual-images-related', args=(self.visual.pk,)))

        self.assertEqual(related.status_code, 200)
        self.assertEqual(len(related.data), 10)
        self.assertIn(str(self.related_visual.pk), {item['id'] for item in related.data})
        self.assertNotIn(str(self.unrelated_visual.pk), {item['id'] for item in related.data})

    def test_episode_detail_exposes_its_parent_serie_information(self):
        response = self.client.get(reverse('episodes-detail', args=(self.episode.pk,)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['serie_title'], self.serie.title)
        self.assertEqual(response.data['serie_description'], self.serie.description)
        self.assertEqual(response.data['owner']['display_name'], 'Film Creator')


class CreatorDashboardAPITests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username='dashboard_creator',
            password='JaxmoraPass2026!',
            first_name='Dashboard',
            other_name='Creator',
            email='dashboard-creator@example.com',
            email_address='dashboard-creator@example.com',
            phone_number='+250788000104',
        )
        self.audience_member = get_user_model().objects.create_user(
            username='dashboard_audience',
            password='JaxmoraPass2026!',
            first_name='Audience',
            other_name='Member',
            email='dashboard-audience@example.com',
            email_address='dashboard-audience@example.com',
            phone_number='+250788000105',
        )
        self.movie = Movie.objects.create(
            owner=self.owner,
            title='Manageable movie',
            description='A movie that the creator can manage from the dashboard.',
            price='1200.00',
            video=SimpleUploadedFile('manageable.mp4', b'video-content'),
            year_released=2026,
            category='Drama',
        )
        self.serie = Serie.objects.create(
            owner=self.owner,
            title='Manageable serie',
            description='A serie ready for additional seasons.',
            price='2500.00',
            year_released=2026,
            category='Drama',
        )
        self.season = Season.objects.create(
            serie=self.serie,
            ref_number=1,
            name='Opening season',
            year_released=2026,
        )
        self.episode = Episode.objects.create(
            season=self.season,
            name='Pilot',
            ref_number=1,
            video=SimpleUploadedFile('pilot.mp4', b'video-content'),
        )
        MovieView.objects.create(movie=self.movie, viewer=self.audience_member)
        MovieLike.objects.create(movie=self.movie, liker=self.audience_member)
        MovieComment.objects.create(
            movie=self.movie,
            commenter=self.audience_member,
            content='I loved this story.',
        )
        EpisodeView.objects.create(episode=self.episode, viewer=self.audience_member)
        self.client.force_authenticate(self.owner)

    def test_dashboard_lists_manageable_content_and_people_who_engaged(self):
        dashboard = self.client.get(reverse('dashboard'))

        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.data['total_uploads'], 2)
        movie = next(item for item in dashboard.data['contents'] if item['type'] == 'movie')
        self.assertEqual(movie['like_count'], 1)
        self.assertEqual(movie['comment_count'], 1)
        self.assertEqual(movie['view_count'], 1)
        serie = next(item for item in dashboard.data['contents'] if item['type'] == 'serie')
        self.assertEqual(serie['seasons'][0]['episodes'][0]['name'], 'Pilot')

        engagement = self.client.get(
            reverse('dashboard_content_engagement', args=('movie', self.movie.pk))
        )
        self.assertEqual(engagement.status_code, 200)
        self.assertEqual(engagement.data['engagements']['views']['people'][0]['display_name'], 'Audience Member')
        self.assertEqual(engagement.data['engagements']['comments']['people'][0]['comment'], 'I loved this story.')

    def test_creator_can_manage_content_and_expand_a_serie(self):
        rename = self.client.patch(
            reverse('movies-detail', args=(self.movie.pk,)),
            {'title': 'Renamed movie'},
            format='json',
        )
        self.assertEqual(rename.status_code, 200)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, 'Renamed movie')

        added_season = self.client.post(
            reverse('series-add-season', args=(self.serie.pk,)),
            {
                'season_number': 2,
                'season_name': 'Second season',
                'season_year': 2027,
                'episodes': '[{"name": "Return", "ref_number": 1}]',
                'episode_file_0': SimpleUploadedFile('return.mp4', b'video-content'),
            },
            format='multipart',
        )
        self.assertEqual(added_season.status_code, 201, added_season.data)
        second_season = self.serie.seasons.get(ref_number=2)
        self.assertEqual(second_season.episodes.get().name, 'Return')

        added_episode = self.client.post(
            reverse('series-add-episodes', args=(self.serie.pk, second_season.pk)),
            {
                'name': 'Second return',
                'ref_number': 2,
                'video': SimpleUploadedFile('return-two.mp4', b'video-content'),
            },
            format='multipart',
        )
        self.assertEqual(added_episode.status_code, 201)
        self.assertEqual(second_season.episodes.count(), 2)
        self.serie.refresh_from_db()
        self.assertGreater(self.serie.uploaded_at, self.movie.uploaded_at)

        deleted_episode = self.client.delete(reverse('episodes-detail', args=(self.episode.pk,)))
        self.assertEqual(deleted_episode.status_code, 204)
        self.assertFalse(Episode.objects.filter(pk=self.episode.pk).exists())

    def test_new_episode_moves_its_serie_to_the_top_of_recent_uploads(self):
        now = timezone.now()
        Serie.objects.filter(pk=self.serie.pk).update(uploaded_at=now - timedelta(days=2))
        Movie.objects.filter(pk=self.movie.pk).update(uploaded_at=now - timedelta(days=1))

        response = self.client.post(
            reverse('series-add-episodes', args=(self.serie.pk, self.season.pk)),
            {
                'name': 'A newer episode',
                'ref_number': 2,
                'video': SimpleUploadedFile('newer.mp4', b'video-content'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        dashboard = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard.data['recent_uploads'][0]['id'], str(self.serie.pk))
        self.assertEqual(dashboard.data['recent_uploads'][0]['type'], 'serie')

    def test_content_upload_returns_the_uploaded_thumbnail(self):
        response = self.client.post(
            reverse('content_upload'),
            {
                'content_type': 'movie',
                'title': 'A thumbnail-backed movie',
                'description': 'A movie with a cover image for content cards.',
                'price': '1500.00',
                'year_released': 2026,
                'category': 'Drama',
                'thumbnail': SimpleUploadedFile(
                    'movie-cover.gif',
                    b64decode('R0lGODlhAQABAIABAP///wAAACwAAAAAAQABAAACAkQBADs='),
                    content_type='image/gif',
                ),
                'content_file': SimpleUploadedFile('movie.mp4', b'video-content'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn('/thumbnails/', response.data['thumbnail'])

    def test_series_upload_accepts_multiple_initial_seasons(self):
        response = self.client.post(
            reverse('serie_upload'),
            {
                'title': 'Multi-season serie',
                'description': 'Uploaded with two seasons at once.',
                'price': '4000.00',
                'year_released': 2026,
                'category': 'Drama',
                'thumbnail': SimpleUploadedFile(
                    'serie-cover.gif',
                    b64decode('R0lGODlhAQABAIABAP///wAAACwAAAAAAQABAAACAkQBADs='),
                    content_type='image/gif',
                ),
                'seasons': (
                    '[{"season_number": 1, "season_name": "One", "season_year": 2026, '
                    '"episodes": [{"name": "One", "ref_number": 1}]}, '
                    '{"season_number": 2, "season_name": "Two", "season_year": 2027, '
                    '"episodes": [{"name": "Two", "ref_number": 1}]}]'
                ),
                'season_0_episode_file_0': SimpleUploadedFile('one.mp4', b'video-content'),
                'season_1_episode_file_0': SimpleUploadedFile('two.mp4', b'video-content'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['title'], 'Multi-season serie')
        self.assertIn('/thumbnails/', response.data['thumbnail'])
        self.assertEqual(len(response.data['seasons']), 2)
