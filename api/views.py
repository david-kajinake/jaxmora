from rest_framework import generics, permissions, status, viewsets
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
    ComedyView,
    Movie,
    MovieLike,
    MovieView,
    Music,
    MusicLike,
    MusicView,
    Serie,
    User,
    UserPreferences,
    VisualImage,
    VisualImageLike,
    VisualImageView,
)
from .serializers import (
    ChangePasswordSerializer,
    ComedySerializer,
    ContentUploadSerializer,
    CurrentUserSerializer,
    MovieSerializer,
    MusicSerializer,
    RegisterSerializer,
    SerieSerializer,
    SerieUploadSerializer,
    UserPreferencesSerializer,
    UserSerializer,
    VisualImageSerializer,
)


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
    def get(self, request):
        total_views = sum(
            model.objects.filter(**lookup).count()
            for model, lookup in (
                (MovieView, {'movie__owner': request.user}),
                (MusicView, {'music__owner': request.user}),
                (ComedyView, {'comedy__owner': request.user}),
                (VisualImageView, {'image__owner': request.user}),
            )
        )
        total_likes = sum(
            model.objects.filter(**lookup).count()
            for model, lookup in (
                (MovieLike, {'movie__owner': request.user}),
                (MusicLike, {'music__owner': request.user}),
                (ComedyLike, {'comedy__owner': request.user}),
                (VisualImageLike, {'image__owner': request.user}),
            )
        )
        uploads = [
            *(
                {'type': 'Movie', 'title': item.title, 'uploaded_at': item.uploaded_at}
                for item in Movie.objects.filter(owner=request.user)
            ),
            *(
                {'type': 'Series', 'title': item.title, 'uploaded_at': item.uploaded_at}
                for item in Serie.objects.filter(owner=request.user)
            ),
            *(
                {'type': 'Music', 'title': item.title, 'uploaded_at': item.uploaded_at}
                for item in Music.objects.filter(owner=request.user)
            ),
            *(
                {'type': 'Comedy', 'title': item.title, 'uploaded_at': item.uploaded_at}
                for item in Comedy.objects.filter(owner=request.user)
            ),
            *(
                {'type': 'Visual', 'title': item.title, 'uploaded_at': item.uploaded_at}
                for item in VisualImage.objects.filter(owner=request.user)
            ),
        ]
        uploads.sort(key=lambda item: item['uploaded_at'], reverse=True)
        return Response(
            {
                'total_views': total_views,
                'total_likes': total_likes,
                'total_uploads': len(uploads),
                'recent_uploads': uploads[:5],
            }
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

class OwnedMediaViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MovieViewSet(OwnedMediaViewSet):
    queryset = Movie.objects.select_related('owner').all()
    serializer_class = MovieSerializer


class MusicViewSet(OwnedMediaViewSet):
    queryset = Music.objects.select_related('owner').all()
    serializer_class = MusicSerializer


class ComedyViewSet(OwnedMediaViewSet):
    queryset = Comedy.objects.select_related('owner').all()
    serializer_class = ComedySerializer


class VisualImageViewSet(OwnedMediaViewSet):
    queryset = VisualImage.objects.select_related('owner').all()
    serializer_class = VisualImageSerializer


class SerieViewSet(OwnedMediaViewSet):
    queryset = Serie.objects.select_related('owner').prefetch_related('seasons__episodes')
    serializer_class = SerieSerializer
