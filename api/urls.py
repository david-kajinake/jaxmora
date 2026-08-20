from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users',views.UserViewSet, basename= 'users')
router.register('movies', views.MovieViewsSet, basename= 'movies')
router.register('music',views.MusicViewSet, basename= 'music')
router.register('comedies', views.ComedyViewSet, basename= 'comedies')
router.register('visual-images', views.VisualImageViewSet, basename= 'visual-images')


urlpatterns = [
    path("",include(router.urls))
]

