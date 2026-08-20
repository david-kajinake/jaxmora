from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status
from .models import User, Movie, Music, Comedy, VisualImage
from .serializers import (
    UserSerializer , MusicSerializer, MovieSerializer,
    ComedySerializer, VisualImageSerializer
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer   

class MovieViewsSet( viewsets.ModelViewSet ):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MusicViewSet( viewsets.ModelViewSet ):
    queryset = Music.objects.all()
    serializer_class = MusicSerializer

class ComedyViewSet( viewsets.ModelViewSet ):
    queryset = Comedy.objects.all()
    serializer_class = ComedySerializer

class VisualImageViewSet( viewsets.ModelViewSet ):
    queryset = VisualImage.objects.all()
    serializer_class = VisualImageSerializer
