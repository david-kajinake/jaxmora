from rest_framework.serializers import ModelSerializer
from .models import User , Movie , Music , Comedy, VisualImage


class UserSerializer( ModelSerializer ):
    class Meta:
        model = User
        fields  = ["id","first_name","other_name"]


class MovieSerializer( ModelSerializer ):
    class Meta:
        model = Movie
        fields = ["id","owner","title","description","price","uploaded_at","video","trailer_link","production_studio"]


class MusicSerializer( ModelSerializer ):
    class Meta:
        model= Music
        fields = ["id","title","owner"]


class ComedySerializer( ModelSerializer ):
    class Meta:
        model = Comedy
        fields =    ["id","owner","title","description","uploaded_at","video","year_released"]


class VisualImageSerializer( ModelSerializer ):
    class Meta:
        model = VisualImage
    
        fields = ["id","owner","title","category","year_released","description","uploaded_at"]