from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    """Authentication form with attributes suitable for the public UI."""

    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'username',
                'placeholder': 'Enter your username',
            }
        ),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'placeholder': 'Enter your password',
            }
        ),
    )


class SignUpForm(UserCreationForm):
    """Basic account registration; creator onboarding is a later step."""

    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': 'you@example.com',
            }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'autocomplete': 'username',
                    'placeholder': 'Choose a username',
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(
            {
                'autocomplete': 'new-password',
                'placeholder': 'Create a password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'autocomplete': 'new-password',
                'placeholder': 'Repeat your password',
            }
        )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account already uses this email address.')
        return email
