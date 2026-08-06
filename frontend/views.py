from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import redirect, render

from .forms import LoginForm, SignUpForm


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
    return render(request, 'jaxmora/films.html')


def music(request):
    return render(request, 'jaxmora/music.html')


def comedy(request):
    return render(request, 'jaxmora/comedy.html')


def image_visuals(request):
    return render(request, 'jaxmora/image-visuals.html')


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
