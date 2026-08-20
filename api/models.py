from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import generate_ulid


class User(AbstractUser):
    """The application's swappable authentication user model."""

    EMAIL_FIELD = 'email_address'

    id = models.CharField(
        primary_key = True,
        max_length = 255,
        default = generate_ulid,
        editable = False,
    )
    first_name = models.CharField( max_length = 255 )
    other_name = models.CharField( max_length = 255 )
    email_address = models.EmailField( max_length = 255 , unique = True )
    phone_number = models.CharField( max_length = 255 )
    date_joined = models.DateField(auto_now_add=True)
    country = models.CharField(max_length=255, null=True, blank=True)

class Post(models.Model):
    id = models.CharField( max_length= 255, primary_key= True, default= generate_ulid )
    title = models.CharField( max_length= 255, null = False )
    description = models.TextField( max_length= 500)
    price = models.DecimalField( decimal_places= 2, max_digits= 10 )
    uploaded_at = models.DateField( auto_now_add= True )
    updated_at = models.DateField( auto_now= True )
    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Movie(Post):
    owner = models.ForeignKey( User, on_delete= models.CASCADE, related_name ="movies" )
    video = models.FileField( upload_to= 'movie_videos/', null= False )
    year_released = models.IntegerField()
    category = models.CharField( max_length = 255 )
    trailer_link = models.CharField( max_length= 255, null = True )
    production_studio = models.CharField( max_length= 255, null = True )


class Music(Post):
    owner = models.ForeignKey( User, on_delete= models.CASCADE, related_name ="musics" )
    video = models.FileField(upload_to= "music_videos/", null = False)
    year_released = models.IntegerField()
    category = models.CharField( max_length= 255, null = True )# Afro beat/HipHop/Reggae/Rock

class Comedy(Post):
    owner = models.ForeignKey( User, on_delete= models.CASCADE, related_name ="comedies" )
    video = models.FileField(upload_to= "comedy_videos/", null= False)
    year_released = models.IntegerField()




class VisualImage(Post):
    owner = models.ForeignKey( User, on_delete= models.CASCADE, related_name ="visual_images" )
    image = models.FileField(upload_to='visual_images/', null=True, blank=True)
    category = models.CharField( max_length= 255 )
    year_released = models.IntegerField()

    


class MovieLike(models.Model):
    movie = models.ForeignKey(Movie, on_delete= models.CASCADE, related_name= "likes")
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_likes")


class MovieComment(models.Model):
    movie = models.ForeignKey( Movie, on_delete= models.CASCADE, related_name= "comments" )
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_comments")
    content =  models.TextField( max_length= 500 )

class MovieView(models.Model):
    movie = models.ForeignKey( Movie, on_delete= models.CASCADE, related_name= "views" )
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_views")


class MusicLike(models.Model):
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name="likes")
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="music_likes")


class MusicView(models.Model):
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name="views")
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="music_views")



class ComedyLike(models.Model):
    comedy = models.ForeignKey(Comedy, on_delete= models.CASCADE, related_name= "likes")
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comedy_likes")


class ComedyComment(models.Model):
    comedy = models.ForeignKey( Comedy, on_delete= models.CASCADE, related_name= "comments" )
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comedy_comments")
    content =  models.TextField( max_length= 500 )

class ComedyView(models.Model):
    comedy = models.ForeignKey(Comedy, on_delete=models.CASCADE, related_name="views")
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comedy_views")

class VisualImageLike(models.Model):
    image = models.ForeignKey(VisualImage, on_delete= models.CASCADE, related_name= "likes")
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visual_image_likes")


class VisualImageComment(models.Model):
    image = models.ForeignKey( VisualImage, on_delete= models.CASCADE, related_name= "comments" )
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visual_image_comments")
    content =  models.TextField( max_length= 500 )

class VisualImageView(models.Model):
    image = models.ForeignKey( VisualImage, on_delete= models.CASCADE, related_name= "views" )
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visual_image_views")


class UserPreferences(models.Model):
    class Language(models.TextChoices):
        ENGLISH = 'en', 'English'
        KISWAHILI = 'sw', 'Kiswahili'
        KINYARWANDA = 'rw', 'Kinyarwanda'
        FRANCAIS = 'fr', 'Francais'

    class FontSize(models.TextChoices):
        VERY_SMALL = 'very-small', 'Very small'
        SMALL = 'small', 'Small'
        MEDIUM = 'medium', 'Medium'
        LARGE = 'large', 'Large'
        VERY_LARGE = 'very-large', 'Very large'

    class FontFamily(models.TextChoices):
        DM_SANS = 'dm-sans', 'DM Sans'
        INTER = 'inter', 'Inter'
        ARIAL = 'arial', 'Arial'
        GEORGIA = 'georgia', 'Georgia'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
    )
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.ENGLISH,
    )
    font_size = models.CharField(
        max_length=12,
        choices=FontSize.choices,
        default=FontSize.MEDIUM,
    )
    font_family = models.CharField(
        max_length=12,
        choices=FontFamily.choices,
        default=FontFamily.DM_SANS,
    )

    def __str__(self):
        return f'{self.user.username} preferences'
