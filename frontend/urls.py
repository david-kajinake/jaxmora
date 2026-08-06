from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('films/', views.films, name='films'),
    path('music/', views.music, name='music'),
    path('comedy/', views.comedy, name='comedy'),
    path('image-visuals/', views.image_visuals, name='image_visuals'),
    path('creators/', views.creators, name='creators'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('reset-password/', views.password_reset_view, name='password_reset'),
    path(
        'reset-password/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='authentication/password_reset_confirm.html',
            success_url=reverse_lazy('frontend:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset-password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='authentication/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
