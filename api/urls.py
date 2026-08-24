from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views


router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('movies', views.MovieViewSet, basename='movies')
router.register('series', views.SerieViewSet, basename='series')
router.register('music', views.MusicViewSet, basename='music')
router.register('comedies', views.ComedyViewSet, basename='comedies')
router.register('visual-images', views.VisualImageViewSet, basename='visual-images')


urlpatterns = [
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/token/', views.JaxmoraTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', views.JWTLogoutAPIView.as_view(), name='logout'),
    path('auth/me/', views.CurrentUserAPIView.as_view(), name='current_user'),
    path('auth/me/password/', views.ChangePasswordAPIView.as_view(), name='change_password'),
    path('auth/preferences/', views.UserPreferencesAPIView.as_view(), name='preferences'),
    path('content/upload/', views.ContentUploadAPIView.as_view(), name='content_upload'),
    path('series/upload/', views.SerieUploadAPIView.as_view(), name='serie_upload'),
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
