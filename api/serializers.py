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

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'other_name')


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


class OwnedContentSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)


class MovieSerializer(OwnedContentSerializer):
    class Meta:
        model = Movie
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'video', 'category', 'trailer_link', 'production_studio',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class MusicSerializer(OwnedContentSerializer):
    class Meta:
        model = Music
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'video', 'category',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class ComedySerializer(OwnedContentSerializer):
    class Meta:
        model = Comedy
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'video',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class VisualImageSerializer(OwnedContentSerializer):
    class Meta:
        model = VisualImage
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'image', 'category',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at')


class EpisodeSerializer(serializers.ModelSerializer):
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
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Serie
        fields = (
            'id', 'owner', 'title', 'description', 'price', 'year_released',
            'uploaded_at', 'category', 'seasons',
        )
        read_only_fields = ('id', 'owner', 'uploaded_at', 'seasons')


class ContentUploadSerializer(serializers.Serializer):
    content_type = serializers.ChoiceField(
        choices=('movie', 'music', 'comedy', 'visual')
    )
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    year_released = serializers.IntegerField(min_value=1888, max_value=2100)
    category = serializers.CharField(max_length=255, required=False, allow_blank=True)
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


class SerieUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    year_released = serializers.IntegerField(min_value=1888, max_value=2100)
    category = serializers.CharField(max_length=255)
    season_number = serializers.IntegerField(min_value=1)
    season_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    season_year = serializers.IntegerField(min_value=1888, max_value=2100)
    episodes = serializers.JSONField()

    def to_internal_value(self, data):
        mutable_data = data.copy()
        episodes = mutable_data.get('episodes')
        if isinstance(episodes, str):
            try:
                mutable_data['episodes'] = json.loads(episodes)
            except json.JSONDecodeError:
                pass
        return super().to_internal_value(mutable_data)

    def validate_episodes(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('Add at least one episode.')
        serializer = SeriesEpisodeInputSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        numbers = [episode['ref_number'] for episode in serializer.validated_data]
        if len(numbers) != len(set(numbers)):
            raise serializers.ValidationError('Episode numbers must be unique.')

        files = self.context['request'].FILES
        missing_files = [
            index for index in range(len(serializer.validated_data))
            if not files.get(f'episode_file_{index}')
        ]
        if missing_files:
            raise serializers.ValidationError('Each episode needs a video file.')
        return serializer.validated_data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        episodes = validated_data.pop('episodes')
        season_number = validated_data.pop('season_number')
        season_name = validated_data.pop('season_name', '')
        season_year = validated_data.pop('season_year')
        serie = Serie.objects.create(owner=user, **validated_data)
        season = Season.objects.create(
            serie=serie,
            ref_number=season_number,
            name=season_name,
            year_released=season_year,
        )
        files = self.context['request'].FILES
        for index, episode in enumerate(episodes):
            Episode.objects.create(
                season=season,
                name=episode['name'],
                ref_number=episode['ref_number'],
                video=files[f'episode_file_{index}'],
            )
        return serie
