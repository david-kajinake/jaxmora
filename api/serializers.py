import json

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import (
    Comedy,
    Episode,
    Movie,
    Music,
    Season,
    Serie,
    User,
    UserPreferences,
    VisualImage,
)


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ('language', 'font_size', 'font_family')


class UserSerializer(serializers.ModelSerializer):
    """Safe public identity used by content responses."""

    display_name = serializers.SerializerMethodField()

    def get_display_name(self, user):
        return ' '.join(part for part in (user.first_name, user.other_name) if part).strip() or 'JAXMORA creator'

    class Meta:
        model = User
        fields = ('id', 'display_name', 'first_name', 'other_name', 'country')


class CurrentUserSerializer(serializers.ModelSerializer):
    preferences = UserPreferencesSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'other_name',
            'phone_number',
            'email_address',
            'country',
            'preferences',
        )
        read_only_fields = ('id', 'preferences')

    def validate_email_address(self, value):
        email = value.lower()
        if User.objects.exclude(pk=self.instance.pk).filter(
            email_address__iexact=email
        ).exists():
            raise serializers.ValidationError('An account already uses this email address.')
        return email

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if 'email_address' in validated_data:
            user.email = user.email_address
            user.save(update_fields=('email',))
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirmation = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'other_name',
            'email_address',
            'phone_number',
            'country',
            'password',
            'password_confirmation',
        )

    def validate_email_address(self, value):
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(
                {'password_confirmation': 'Passwords do not match.'}
            )
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        email = validated_data['email_address']
        return User.objects.create_user(
            email=email,
            password=password,
            **validated_data,
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirmation = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Your current password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirmation']:
            raise serializers.ValidationError(
                {'new_password_confirmation': 'Passwords do not match.'}
            )
        validate_password(attrs['new_password'], self.context['request'].user)
        return attrs


class ViewCountSerializerMixin:
    def get_view_count(self, content):
        return content.views.values('viewer_id').distinct().count()


class EngagementCountSerializerMixin(serializers.Serializer):
    is_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    def get_like_count(self, content):
        return content.likes.count()

    def get_comment_count(self, content):
        return content.comments.count()

    def get_is_liked(self, content):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return content.likes.filter(liker=request.user).exists()
        return False

class OwnedContentSerializer(ViewCountSerializerMixin, serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)


class MovieSerializer(EngagementCountSerializerMixin, OwnedContentSerializer):
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'thumbnail', 'video', 'category', 'trailer_link', 'production_studio',
            'view_count', 'like_count', 'comment_count', 'is_liked',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class MusicSerializer(EngagementCountSerializerMixin, OwnedContentSerializer):
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Music
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'thumbnail', 'video', 'category', 'view_count', 'like_count',
            'comment_count', 'is_liked',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class ComedySerializer(EngagementCountSerializerMixin, OwnedContentSerializer):
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Comedy
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'thumbnail', 'video', 'view_count', 'like_count', 'comment_count', 'is_liked',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class VisualImageSerializer(EngagementCountSerializerMixin, OwnedContentSerializer):
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = VisualImage
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'thumbnail', 'image', 'category', 'view_count', 'like_count',
            'comment_count', 'is_liked',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class EpisodeSerializer(
    EngagementCountSerializerMixin, ViewCountSerializerMixin, serializers.ModelSerializer
):
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    owner = UserSerializer(source='season.serie.owner', read_only=True)
    season_id = serializers.CharField(source='season.id', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    season_ref_number = serializers.IntegerField(source='season.ref_number', read_only=True)
    season_year_released = serializers.IntegerField(source='season.year_released', read_only=True)
    serie_id = serializers.CharField(source='season.serie.id', read_only=True)
    serie_title = serializers.CharField(source='season.serie.title', read_only=True)
    serie_description = serializers.CharField(source='season.serie.description', read_only=True)
    serie_category = serializers.CharField(source='season.serie.category', read_only=True)
    serie_price = serializers.DecimalField(
        source='season.serie.price', max_digits=10, decimal_places=2, read_only=True
    )
    serie_year_released = serializers.IntegerField(source='season.serie.year_released', read_only=True)
    serie_uploaded_at = serializers.DateTimeField(source='season.serie.uploaded_at', read_only=True)

    class Meta:
        model = Episode
        fields = (
            'id', 'name', 'ref_number', 'video', 'uploaded_at', 'view_count',
            'like_count', 'comment_count',
            'owner', 'season_id', 'season_name', 'season_ref_number',
            'season_year_released', 'serie_id', 'serie_title',
            'serie_description', 'serie_category', 'serie_price',
            'serie_year_released', 'serie_uploaded_at', 'is_liked',
        )
        read_only_fields = ('id', 'uploaded_at')


class EpisodeManagementSerializer(serializers.ModelSerializer):
    """Fields a creator may change on an existing episode."""

    class Meta:
        model = Episode
        fields = ('id', 'name', 'ref_number', 'video', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')


class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = (
            'id', 'ref_number', 'name', 'year_released', 'uploaded_at', 'episodes',
        )
        read_only_fields = ('id', 'uploaded_at')


class SerieSerializer(OwnedContentSerializer):
    view_count = serializers.SerializerMethodField()
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Serie
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'thumbnail', 'category', 'seasons', 'view_count',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at', 'seasons')

class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    commenter = UserSerializer(read_only=True)
    content = serializers.CharField(max_length=500)


class ContentUploadSerializer(serializers.Serializer):
    content_type = serializers.ChoiceField(
        choices=('movie', 'music', 'comedy', 'visual')
    )
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    year_released = serializers.IntegerField(min_value=1888, max_value=2100)
    category = serializers.CharField(max_length=255, required=False, allow_blank=True)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
    content_file = serializers.FileField()
    trailer_link = serializers.CharField(max_length=255, required=False, allow_blank=True)
    production_studio = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    def validate(self, attrs):
        if attrs['content_type'] in ('movie', 'visual') and not attrs.get('category'):
            raise serializers.ValidationError({'category': 'Category is required.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        content_type = validated_data.pop('content_type')
        content_file = validated_data.pop('content_file')
        category = validated_data.pop('category', '')
        trailer_link = validated_data.pop('trailer_link', '')
        production_studio = validated_data.pop('production_studio', '')
        common_fields = {'owner': user, **validated_data}

        if content_type == 'movie':
            return Movie.objects.create(
                **common_fields,
                video=content_file,
                category=category,
                trailer_link=trailer_link or None,
                production_studio=production_studio or None,
            )
        if content_type == 'music':
            return Music.objects.create(
                **common_fields, video=content_file, category=category or None
            )
        if content_type == 'comedy':
            return Comedy.objects.create(**common_fields, video=content_file)
        return VisualImage.objects.create(
            **common_fields, image=content_file, category=category
        )


class SeriesEpisodeInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    ref_number = serializers.IntegerField(min_value=1)


class SeriesSeasonInputSerializer(serializers.Serializer):
    season_number = serializers.IntegerField(min_value=1)
    season_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    season_year = serializers.IntegerField(min_value=1888, max_value=2100)
    episodes = SeriesEpisodeInputSerializer(many=True, allow_empty=False)


class SerieUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    year_released = serializers.IntegerField(min_value=1888, max_value=2100)
    category = serializers.CharField(max_length=255)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
    season_number = serializers.IntegerField(min_value=1, required=False)
    season_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    season_year = serializers.IntegerField(min_value=1888, max_value=2100, required=False)
    episodes = serializers.CharField(required=False)
    seasons = serializers.CharField(required=False)

    def validate_episodes(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                raise serializers.ValidationError('Value must be valid JSON.') from error
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('Add at least one episode.')
        serializer = SeriesEpisodeInputSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        numbers = [episode['ref_number'] for episode in serializer.validated_data]
        if len(numbers) != len(set(numbers)):
            raise serializers.ValidationError('Episode numbers must be unique.')

        return serializer.validated_data

    def validate(self, attrs):
        seasons = attrs.get('seasons')
        files = self.context['request'].FILES
        if seasons is not None:
            try:
                seasons = json.loads(seasons) if isinstance(seasons, str) else seasons
            except json.JSONDecodeError as error:
                raise serializers.ValidationError(
                    {'seasons': 'Value must be valid JSON.'}
                ) from error
            if not isinstance(seasons, list) or not seasons:
                raise serializers.ValidationError({'seasons': 'Add at least one season.'})
            serializer = SeriesSeasonInputSerializer(data=seasons, many=True)
            serializer.is_valid(raise_exception=True)
            season_numbers = [season['season_number'] for season in serializer.validated_data]
            if len(season_numbers) != len(set(season_numbers)):
                raise serializers.ValidationError({'seasons': 'Season numbers must be unique.'})
            for season_index, season in enumerate(serializer.validated_data):
                episode_numbers = [episode['ref_number'] for episode in season['episodes']]
                if len(episode_numbers) != len(set(episode_numbers)):
                    raise serializers.ValidationError(
                        {'seasons': f'Episode numbers must be unique in season {season["season_number"]}.'}
                    )
                for episode_index in range(len(season['episodes'])):
                    if not files.get(f'season_{season_index}_episode_file_{episode_index}'):
                        raise serializers.ValidationError(
                            {'seasons': 'Each episode needs a video file.'}
                        )
            attrs['seasons'] = serializer.validated_data
            return attrs

        required_legacy_fields = ('season_number', 'season_year', 'episodes')
        missing = [field for field in required_legacy_fields if field not in attrs]
        if missing:
            raise serializers.ValidationError(
                {'seasons': 'Add at least one season with one or more episodes.'}
            )
        for index in range(len(attrs['episodes'])):
            if not files.get(f'episode_file_{index}'):
                raise serializers.ValidationError({'episodes': 'Each episode needs a video file.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        seasons = validated_data.pop('seasons', None)
        uses_season_payload = seasons is not None
        if seasons is None:
            seasons = [{
                'season_number': validated_data.pop('season_number'),
                'season_name': validated_data.pop('season_name', ''),
                'season_year': validated_data.pop('season_year'),
                'episodes': validated_data.pop('episodes'),
            }]
        serie = Serie.objects.create(owner=user, **validated_data)
        files = self.context['request'].FILES
        for season_index, season_data in enumerate(seasons):
            season = Season.objects.create(
                serie=serie,
                ref_number=season_data['season_number'],
                name=season_data.get('season_name', ''),
                year_released=season_data['season_year'],
            )
            for episode_index, episode in enumerate(season_data['episodes']):
                file_key = (
                    f'season_{season_index}_episode_file_{episode_index}'
                    if uses_season_payload else f'episode_file_{episode_index}'
                )
                Episode.objects.create(
                    season=season,
                    name=episode['name'],
                    ref_number=episode['ref_number'],
                    video=files[file_key],
                )
        return serie


class SeasonUploadSerializer(serializers.Serializer):
    """One new season and its initial episodes for an existing series."""

    season_number = serializers.IntegerField(min_value=1)
    season_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    season_year = serializers.IntegerField(min_value=1888, max_value=2100)
    episodes = serializers.CharField()

    def validate_episodes(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                raise serializers.ValidationError('Value must be valid JSON.') from error
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('Add at least one episode.')
        serializer = SeriesEpisodeInputSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        numbers = [episode['ref_number'] for episode in serializer.validated_data]
        if len(numbers) != len(set(numbers)):
            raise serializers.ValidationError('Episode numbers must be unique.')
        for index in range(len(serializer.validated_data)):
            if not self.context['request'].FILES.get(f'episode_file_{index}'):
                raise serializers.ValidationError('Each episode needs a video file.')
        return serializer.validated_data


class EpisodeUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    ref_number = serializers.IntegerField(min_value=1)
    video = serializers.FileField()


class SeasonManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ('id', 'ref_number', 'name', 'year_released', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')


EngagementCountSerializerMixin