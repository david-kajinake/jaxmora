from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import redirect, render

from .forms import LoginForm, SignUpForm


def home(request):
    """Render the public landing page.
    The cards are presentation data for the first frontend milestone.  They
    deliberately mirror the shape of the marketplace resources that the DRF
    API will expose, so the template can later be populated from the API.
    """
    return render(request, 'jaxmora/home.html')


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
