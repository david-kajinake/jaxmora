from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Comedy,
    ComedyLike,
    ComedyComment,
    ComedyView,
    ContentReport,
    Episode,
    EpisodeView,
    Movie,
    MovieComment,
    MovieLike,
    MovieView,
    Music,
    MusicLike,
    MusicComment,
    MusicView,
    Season,
    Serie,
    SerieView,
    User,
    UserPreferences,
    VisualImage,
    VisualImageComment,
    VisualImageLike,
    VisualImageView,
)
from .serializers import (
    ChangePasswordSerializer,
    ComedySerializer,
    ContentUploadSerializer,
    CurrentUserSerializer,
    EpisodeSerializer,
    EpisodeManagementSerializer,
    EpisodeUploadSerializer,
    MovieSerializer,
    MusicSerializer,
    RegisterSerializer,
    SerieSerializer,
    SerieUploadSerializer,
    SeasonManagementSerializer,
    SeasonSerializer,
    SeasonUploadSerializer,
    UserPreferencesSerializer,
    UserSerializer,
    VisualImageSerializer,
)
from .search_strategies import get_search_strategy


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.owner_id == request.user.id


class JaxmoraTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Keep JWT claims useful to the frontend without exposing account data."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class JaxmoraTokenObtainPairView(TokenObtainPairView):
    serializer_class = JaxmoraTokenObtainPairSerializer


class RegisterAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class CurrentUserAPIView(APIView):
    def get(self, request):
        UserPreferences.objects.get_or_create(user=request.user)
        return Response(CurrentUserSerializer(request.user).data)

    def patch(self, request):
        serializer = CurrentUserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        if username != request.user.username:
            return Response(
                {'username': ['Enter your username exactly to confirm deletion.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(password):
            return Response(
                {'password': ['Your current password is incorrect.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordAPIView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=('password',))
        return Response({'detail': 'Password updated.'})


class UserPreferencesAPIView(APIView):
    def get_object(self):
        preferences, _ = UserPreferences.objects.get_or_create(user=self.request.user)
        return preferences

    def get(self, request):
        return Response(UserPreferencesSerializer(self.get_object()).data)

    def put(self, request):
        serializer = UserPreferencesSerializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    patch = put


class JWTLogoutAPIView(APIView):
    """Blacklist the supplied refresh token and leave access-token cleanup to the client."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'refresh': ['This field is required.']}, status=400)
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response({'refresh': ['Token is invalid or expired.']}, status=400)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ContentUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = ContentUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        content = serializer.save()
        serializer_map = {
            Movie: MovieSerializer,
            Music: MusicSerializer,
            Comedy: ComedySerializer,
            VisualImage: VisualImageSerializer,
        }
        return Response(serializer_map[type(content)](content).data, status=status.HTTP_201_CREATED)


class SerieUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = SerieUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serie = serializer.save()
        return Response(SerieSerializer(serie).data, status=status.HTTP_201_CREATED)


class DashboardAPIView(APIView):
    """Creator-facing overview, including the full managed content library."""

    CONTENT_TYPES = {
        'movie': {
            'label': 'Movie', 'model': Movie, 'serializer': MovieSerializer,
            'view_model': MovieView, 'view_lookup': 'movie',
            'like_model': MovieLike, 'like_lookup': 'movie',
            'comment_model': MovieComment, 'comment_lookup': 'movie',
        },
        'serie': {
            'label': 'Serie', 'model': Serie, 'serializer': SerieSerializer,
            'view_model': SerieView, 'view_lookup': 'serie',
        },
        'music': {
            'label': 'Music', 'model': Music, 'serializer': MusicSerializer,
            'view_model': MusicView, 'view_lookup': 'music',
            'like_model': MusicLike, 'like_lookup': 'music',
        },
        'comedy': {
            'label': 'Comedy', 'model': Comedy, 'serializer': ComedySerializer,
            'view_model': ComedyView, 'view_lookup': 'comedy',
            'like_model': ComedyLike, 'like_lookup': 'comedy',
            'comment_model': ComedyComment, 'comment_lookup': 'comedy',
        },
        'visual': {
            'label': 'Visual image', 'model': VisualImage, 'serializer': VisualImageSerializer,
            'view_model': VisualImageView, 'view_lookup': 'image',
            'like_model': VisualImageLike, 'like_lookup': 'image',
            'comment_model': VisualImageComment, 'comment_lookup': 'image',
        },
        'episode': {
            'label': 'Episode', 'model': Episode, 'serializer': EpisodeSerializer,
            'view_model': EpisodeView, 'view_lookup': 'episode',
        },
    }

    @classmethod
    def content_summary(cls, content_type, item):
        config = cls.CONTENT_TYPES[content_type]
        data = config['serializer'](item).data
        return {
            'id': str(item.pk),
            'type': content_type,
            'label': config['label'],
            'title': getattr(item, 'title', getattr(item, 'name', 'Untitled content')),
            'uploaded_at': item.uploaded_at,
            'view_count': data.get('view_count', 0),
            'like_count': cls.engagement_count(config, item, 'like'),
            'comment_count': cls.engagement_count(config, item, 'comment'),
            'seasons': data.get('seasons', []),
        }

    @staticmethod
    def engagement_count(config, item, kind):
        model = config.get(f'{kind}_model')
        lookup = config.get(f'{kind}_lookup')
        return model.objects.filter(**{lookup: item}).count() if model else 0

    def get(self, request):
        contents = []
        for content_type, config in self.CONTENT_TYPES.items():
            queryset = config['model'].objects
            if content_type == 'episode':
                items = queryset.filter(season__serie__owner=request.user).select_related(
                    'season__serie__owner'
                )
            else:
                items = queryset.filter(owner=request.user)
                if content_type == 'serie':
                    items = items.prefetch_related('seasons__episodes')
            contents.extend(
                self.content_summary(content_type, item) for item in items
            )
        contents.sort(key=lambda item: item['uploaded_at'], reverse=True)

        # Episodes are managed within their parent series, so they do not inflate
        # the published-content total or duplicate the series in the main library.
        uploads = [item for item in contents if item['type'] != 'episode']
        total_views = sum(item['view_count'] for item in contents)
        total_likes = sum(item['like_count'] for item in contents)
        return Response(
            {
                'total_views': total_views,
                'total_likes': total_likes,
                'total_uploads': len(uploads),
                'recent_uploads': uploads[:5],
                'contents': uploads,
            }
        )


class DashboardEngagementAPIView(APIView):
    """Show a creator the people who engaged with one of their uploads."""

    def get_content(self, request, content_type, content_id):
        config = DashboardAPIView.CONTENT_TYPES.get(content_type)
        if not config:
            return None, None
        queryset = config['model'].objects
        owner_lookup = {'season__serie__owner': request.user} if content_type == 'episode' else {'owner': request.user}
        return config, get_object_or_404(queryset.filter(**owner_lookup), pk=content_id)

    @staticmethod
    def people(records, relation_field, include_comment=False):
        people = []
        seen = set()
        for record in records.select_related(relation_field):
            user = getattr(record, relation_field)
            if include_comment:
                people.append({
                    'user': UserSerializer(user).data,
                    'comment': record.content,
                })
            elif user.pk not in seen:
                seen.add(user.pk)
                people.append(UserSerializer(user).data)
        return people

    def get(self, request, content_type, content_id):
        config, content = self.get_content(request, content_type, content_id)
        if config is None:
            return Response({'detail': 'Unknown content type.'}, status=status.HTTP_404_NOT_FOUND)

        engagements = {}
        for kind, person_field in (('view', 'viewer'), ('like', 'liker'), ('comment', 'commenter')):
            model = config.get(f'{kind}_model')
            lookup = config.get(f'{kind}_lookup')
            records = model.objects.filter(**{lookup: content}) if model else []
            people = self.people(records, person_field, include_comment=kind == 'comment') if model else []
            engagements[f'{kind}s'] = {'count': len(people) if kind != 'comment' else len(people), 'people': people}

        return Response({
            'content': DashboardAPIView.content_summary(content_type, content),
            'engagements': engagements,
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

class OwnedMediaViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        """Remove the uploaded asset as well as its database record."""
        for asset_name in ('video', 'image', 'thumbnail'):
            asset = getattr(instance, asset_name, None)
            if asset:
                asset.delete(save=False)
        instance.delete()


class ViewedContentViewSet(OwnedMediaViewSet):
    """Public catalogue content with optional, per-user view tracking."""

    view_model = None
    view_relation_field = None

    @action(
        detail=True,
        methods=('post',),
        url_path='record-view',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def record_view(self, request, pk=None):
        content = self.get_object()
        self.view_model.objects.get_or_create(
            **{self.view_relation_field: content, 'viewer': request.user}
        )
        return Response({'view_count': content.views.values('viewer_id').distinct().count()})

    @action(detail=True, methods=('get',))
    def related(self, request, pk=None):
        content = self.get_object()
        queryset = self.get_related_queryset(content).order_by('-uploaded_at')
        return Response(self.get_serializer(queryset, many=True).data)

    def get_related_queryset(self, content):
        return self.get_queryset().none()

    @action(
        detail= True,
        methods= ('post',),
        url_path= 'like',
        permission_classes = (permissions.IsAuthenticated,),
    )
    def toggle_like(self, request, pk= None):
        content = self.get_object()
        like_obj = self.like_model.objects.filter(
            **{self.like_relation_field: content, 'liker': request.user  }
        ).first()

        if like_obj:
            like_obj.delete()
            liked = False
        else:
            self.like_model.objects.create(
                **{self.like_relation_field: content, 'liker': request.user}
            )
            liked = True

        return Response({
            'liked': liked,
            'like_count': self.like_model.objects.filter(**{self.like_relation_field: content}).count()
        })           

    @action(
        detail= True,
        methods= ('post', 'get'),
        url_path= 'comments',
        permission_classes= (permissions.IsAuthenticatedOrReadOnly,),
    )
    def comments(self, request, pk= None):
        content= self.get_object()
        if request.method == 'POST':
            text = request.data.get('content', '').strip()
            if not text:
                return Response({'content':['Comment cannot be empty!.']}, status= status.HTTP_400_BAD_REQUEST)
            comment = self.comment_model.objects.create(
                **{self.comment_relation_field: content, 'commenter': request.user, 'content': text}
            )
            return Response(
                {
                    'id': comment.pk,
                    'commenter': UserSerializer(request.user).data,
                    'content': comment.content
                },
                status= status.HTTP_201_CREATED
            )

        queryset= self.comment_model.objects.filter(
            **{self.comment_relation_field: content}
        ).select_related('commenter')
        return Response(
            [
                {
                    'id': c.pk,
                    'commenter': UserSerializer(c.commenter).data,
                    'content': c.content,
                } for c in queryset
            ]
        )


class ContentReportAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        reason = request.data.get('reason', '').strip()
        details = request.data.get('details', '').strip()

        if not content_type or not content_id or not reason:
            return Response(
                {'detail': 'content_type, content_id, and reason are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ContentReport.objects.create(
            reporter=request.user,
            content_type=content_type,
            content_id=content_id,
            reason=reason,
            details=details,
        )
        return Response({'detail': 'Report submitted successfully. Thank you!'}, status=status.HTTP_201_CREATED)

class MovieViewSet(ViewedContentViewSet):
    queryset = Movie.objects.select_related('owner').all()
    serializer_class = MovieSerializer
    view_model = MovieView
    view_relation_field = 'movie'
    like_model = MovieLike
    like_relation_field = 'movie'
    comment_model = MovieComment
    comment_relation_field = 'movie'


    def get_related_queryset(self, movie):
        matches = Q()
        if movie.category:
            matches |= Q(category__iexact=movie.category)
        if movie.production_studio:
            matches |= Q(production_studio__iexact=movie.production_studio)
        return self.get_queryset().filter(matches).exclude(pk=movie.pk) if matches else self.get_queryset().none()


class MusicViewSet(ViewedContentViewSet):
    queryset = Music.objects.select_related('owner').all()
    serializer_class = MusicSerializer
    view_model = MusicView
    view_relation_field = 'music'
    like_model = MusicLike
    like_relation_field = 'music'
    comment_model = MusicComment
    comment_relation_field = 'music'


    def get_related_queryset(self, music):
        if not music.category:
            return self.get_queryset().none()
        return self.get_queryset().filter(
            category__iexact=music.category
        ).exclude(pk=music.pk)


class ComedyViewSet(ViewedContentViewSet):
    queryset = Comedy.objects.select_related('owner').all()
    serializer_class = ComedySerializer
    view_model = ComedyView
    view_relation_field = 'comedy'
    like_model = ComedyLike
    like_relation_field = 'comedy'
    comment_model = ComedyComment
    comment_relation_field = 'comedy'

    def get_related_queryset(self, comedy):
        matches = Q(owner=comedy.owner)
        if comedy.owner.country:
            matches |= Q(owner__country__iexact=comedy.owner.country)
        return self.get_queryset().filter(matches).exclude(pk=comedy.pk)


class VisualImageViewSet(ViewedContentViewSet):
    queryset = VisualImage.objects.select_related('owner').all()
    serializer_class = VisualImageSerializer
    view_model = VisualImageView
    view_relation_field = 'image'
    like_model = VisualImageLike
    like_relation_field = 'image'
    comment_model = VisualImageComment
    comment_relation_field = 'image'

    def get_related_queryset(self, image):
        if not image.category:
            return self.get_queryset().none()
        return self.get_queryset().filter(
            category__iexact=image.category
        ).exclude(pk=image.pk)


class SerieViewSet(ViewedContentViewSet):
    queryset = Serie.objects.select_related('owner').prefetch_related('seasons__episodes')
    serializer_class = SerieSerializer
    view_model = SerieView
    view_relation_field = 'serie'


    def perform_destroy(self, instance):
        for season in instance.seasons.prefetch_related('episodes'):
            for episode in season.episodes.all():
                episode.video.delete(save=False)
        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        instance.delete()

    def get_related_queryset(self, serie):
        if not serie.category:
            return self.get_queryset().none()
        return self.get_queryset().filter(
            category__iexact=serie.category
        ).exclude(pk=serie.pk)

    @action(
        detail=True,
        methods=('post',),
        url_path='seasons',
        parser_classes=(MultiPartParser, FormParser),
    )
    @transaction.atomic
    def add_season(self, request, pk=None):
        serie = self.get_object()
        serializer = SeasonUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if serie.seasons.filter(ref_number=data['season_number']).exists():
            return Response(
                {'season_number': ['This series already has that season number.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        season = Season.objects.create(
            serie=serie,
            ref_number=data['season_number'],
            name=data.get('season_name', ''),
            year_released=data['season_year'],
        )
        for index, episode in enumerate(data['episodes']):
            Episode.objects.create(
                season=season,
                name=episode['name'],
                ref_number=episode['ref_number'],
                video=request.FILES[f'episode_file_{index}'],
            )
        serie.uploaded_at = timezone.now()
        serie.save(update_fields=('uploaded_at',))
        return Response(SeasonSerializer(season).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('patch', 'delete'),
        url_path=r'seasons/(?P<season_id>[^/.]+)',
        parser_classes=(MultiPartParser, FormParser, JSONParser),
    )
    def manage_season(self, request, season_id=None, pk=None):
        serie = self.get_object()
        season = get_object_or_404(serie.seasons, pk=season_id)
        if request.method == 'DELETE':
            for episode in season.episodes.all():
                episode.video.delete(save=False)
            season.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SeasonManagementSerializer(season, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if (
            'ref_number' in serializer.validated_data
            and serie.seasons.exclude(pk=season.pk).filter(
                ref_number=serializer.validated_data['ref_number']
            ).exists()
        ):
            return Response(
                {'ref_number': ['This series already has that season number.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(SeasonSerializer(season).data)

    @action(
        detail=True,
        methods=('post',),
        url_path=r'seasons/(?P<season_id>[^/.]+)/episodes',
        parser_classes=(MultiPartParser, FormParser),
    )
    @transaction.atomic
    def add_episodes(self, request, season_id=None, pk=None):
        serie = self.get_object()
        season = get_object_or_404(serie.seasons, pk=season_id)
        serializer = EpisodeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if season.episodes.filter(ref_number=serializer.validated_data['ref_number']).exists():
            return Response(
                {'ref_number': ['This season already has that episode number.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        episode = Episode.objects.create(season=season, **serializer.validated_data)
        serie.uploaded_at = timezone.now()
        serie.save(update_fields=('uploaded_at',))
        return Response(EpisodeSerializer(episode).data, status=status.HTTP_201_CREATED)


class IsEpisodeOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.season.serie.owner_id == request.user.id
        )


class EpisodeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Episode.objects.select_related('season__serie__owner').all()
    serializer_class = EpisodeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsEpisodeOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.action in ('partial_update', 'update'):
            return EpisodeManagementSerializer
        return EpisodeSerializer

    def perform_destroy(self, instance):
        instance.video.delete(save=False)
        instance.delete()

    @action(
        detail=True,
        methods=('post',),
        url_path='record-view',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def record_view(self, request, pk=None):
        episode = self.get_object()
        EpisodeView.objects.get_or_create(episode=episode, viewer=request.user)
        return Response({'view_count': episode.views.values('viewer_id').distinct().count()})


#SEARCH STRATEGIES
class GlobalSearchAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, query):
        clean_query = query.strip()
        if not clean_query:
            return Response({
                'movies': [],
                'music': [],
                'comedies': [],
                'visuals': [],
                'series': [],
            })

        strategy = get_search_strategy()
        results = strategy.search(clean_query, request)
        return Response(results)


    