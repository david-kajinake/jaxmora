from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from api.models import (
    Comedy,
    ComedyLike,
    ComedyView,
    Movie,
    MovieLike,
    MovieView,
    Music,
    MusicLike,
    MusicView,
    UserPreferences,
    VisualImage,
    VisualImageLike,
    VisualImageView,
)

from .forms import (
    AccountDeletionForm,
    ContentUploadForm,
    LoginForm,
    ProfileForm,
    SignUpForm,
    UserSettingsForm,
)


CREATOR_DIRECTORY = [
    {
        'name': 'Aline Mukashyaka',
        'category': 'Movie creator',
        'filter': 'movies',
        'image': 'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Eric Ndahayo',
        'category': 'Movie creator',
        'filter': 'movies',
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Nia Karekezi',
        'category': 'Movie creator',
        'filter': 'movies',
        'image': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Munyaneza David',
        'category': 'Movie creator',
        'filter': 'movies',
        'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Clation Kibonge',
        'category': 'Comedy creator',
        'filter': 'comedy',
        'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Emmy Pro',
        'category': 'Comedy creator',
        'filter': 'comedy',
        'image': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Teta Talks',
        'category': 'Comedy creator',
        'filter': 'comedy',
        'image': 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Roga Roga',
        'category': 'Comedy creator',
        'filter': 'comedy',
        'image': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Innocent Photos',
        'category': 'Visual image creator',
        'filter': 'visual-images',
        'image': 'https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Bella Photography',
        'category': 'Visual image creator',
        'filter': 'visual-images',
        'image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Africa Lens',
        'category': 'Visual image creator',
        'filter': 'visual-images',
        'image': 'https://images.unsplash.com/photo-1542206395-9feb3edaa68d?auto=format&fit=crop&w=300&q=85',
    },
    {
        'name': 'Nuru Studio',
        'category': 'Visual image creator',
        'filter': 'visual-images',
        'image': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=300&q=85',
    },
]


def home(request):
    """Render the public landing page.
    The cards are presentation data for the first frontend milestone.  They
    deliberately mirror the shape of the marketplace resources that the DRF
    API will expose, so the template can later be populated from the API.
    """
    return render(request, 'jaxmora/home.html')


def films(request):
    return render(request, 'jaxmora/films.html', {'catalog_type': 'films'})


def music(request):
    return render(request, 'jaxmora/music.html', {'catalog_type': 'music'})


def comedy(request):
    return render(request, 'jaxmora/comedy.html', {'catalog_type': 'comedy'})


def image_visuals(request):
    return render(request, 'jaxmora/image-visuals.html', {'catalog_type': 'visuals'})


def creators(request):
    """Render non-musician marketplace creators for the public directory."""
    return render(
        request,
        'jaxmora/creators.html',
        {'creators': CREATOR_DIRECTORY},
    )


def login_view(request):
    """Sign an existing customer or creator into JAXMORA."""
    if request.user.is_authenticated:
        return redirect('frontend:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Welcome back to JAXMORA.')
        return redirect('frontend:home')

    return render(request, 'authentication/login.html', {'form': form})


def signup_view(request):
    """Create a new marketplace account and start an authenticated session."""
    if request.user.is_authenticated:
        return redirect('frontend:home')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your JAXMORA account is ready.')
        return redirect('frontend:home')

    return render(request, 'authentication/signup.html', {'form': form})


def password_reset_view(request):
    """Request a password-reset email without exposing account existence."""
    form = PasswordResetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(
            request=request,
            email_template_name='authentication/password_reset_email.txt',
            subject_template_name='authentication/password_reset_subject.txt',
        )
        messages.success(
            request,
            'If that email belongs to an account, a reset link is on its way.',
        )
        return redirect('frontend:password_reset')

    return render(request, 'authentication/reset-password.html', {'form': form})


@login_required
def dashboard(request):
    """Show creator analytics and accept a new marketplace upload."""
    upload_form = ContentUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and upload_form.is_valid():
        data = upload_form.cleaned_data
        common_fields = {
            'owner': request.user,
            'title': data['title'],
            'description': data['description'],
            'price': data['price'],
            'year_released': data['year_released'],
        }
        if data['content_type'] == 'movie':
            Movie.objects.create(
                **common_fields,
                video=data['content_file'],
                category=data['category'],
                trailer_link=data['trailer_link'] or None,
                production_studio=data['production_studio'] or None,
            )
        elif data['content_type'] == 'music':
            Music.objects.create(
                **common_fields,
                video=data['content_file'],
                category=data['category'] or None,
            )
        elif data['content_type'] == 'comedy':
            Comedy.objects.create(**common_fields, video=data['content_file'])
        else:
            VisualImage.objects.create(
                **common_fields,
                image=data['content_file'],
                category=data['category'],
            )
        messages.success(request, 'Your content has been uploaded and is ready to manage.')
        return redirect('frontend:dashboard')

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
            {
                'type': 'Film',
                'title': item.title,
                'uploaded_at': item.uploaded_at,
            }
            for item in Movie.objects.filter(owner=request.user)
        ),
        *(
            {
                'type': 'Music',
                'title': item.title,
                'uploaded_at': item.uploaded_at,
            }
            for item in Music.objects.filter(owner=request.user)
        ),
        *(
            {
                'type': 'Comedy',
                'title': item.title,
                'uploaded_at': item.uploaded_at,
            }
            for item in Comedy.objects.filter(owner=request.user)
        ),
        *(
            {
                'type': 'Visual',
                'title': item.title,
                'uploaded_at': item.uploaded_at,
            }
            for item in VisualImage.objects.filter(owner=request.user)
        ),
    ]
    uploads.sort(key=lambda item: item['uploaded_at'], reverse=True)
    return render(
        request,
        'jaxmora/dashboard.html',
        {
            'upload_form': upload_form,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_uploads': len(uploads),
            'recent_uploads': uploads[:5],
        },
    )


@login_required
def profile(request):
    """Update account information, credentials, or permanently delete an account."""
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    deletion_form = AccountDeletionForm(request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'profile':
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile details have been updated.')
                return redirect('frontend:profile')
        elif action == 'password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been changed.')
                return redirect('frontend:profile')
        elif action == 'delete':
            deletion_form = AccountDeletionForm(request.user, request.POST)
            if deletion_form.is_valid():
                username = request.user.username
                request.user.delete()
                logout(request)
                messages.success(request, f'{username}, your JAXMORA account has been deleted.')
                return redirect('frontend:home')

    return render(
        request,
        'jaxmora/profile.html',
        {
            'profile_form': profile_form,
            'password_form': password_form,
            'deletion_form': deletion_form,
        },
    )


@login_required
def settings(request):
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)
    settings_form = UserSettingsForm(request.POST or None, instance=preferences)
    if request.method == 'POST' and settings_form.is_valid():
        settings_form.save()
        messages.success(request, 'Your display settings have been saved.')
        return redirect('frontend:settings')
    return render(request, 'jaxmora/settings.html', {'settings_form': settings_form})


def privacy_policy(request):
    return render(
        request,
        'jaxmora/legal.html',
        {'legal_title': 'Privacy policy', 'legal_kind': 'privacy'},
    )


def terms_of_service(request):
    return render(
        request,
        'jaxmora/legal.html',
        {'legal_title': 'Terms of service', 'legal_kind': 'terms'},
    )


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have signed out of JAXMORA.')
    return redirect('frontend:home')
