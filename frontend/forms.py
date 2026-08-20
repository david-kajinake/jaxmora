from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from api.models import UserPreferences


User = get_user_model()


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

    first_name = forms.CharField(
        label='First name',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'given-name',
                'placeholder': 'Enter your first name',
            }
        ),
    )
    other_name = forms.CharField(
        label='Other name',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'family-name',
                'placeholder': 'Enter your other name',
            }
        ),
    )
    email_address = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': 'you@example.com',
            }
        ),
    )
    phone_number = forms.CharField(
        label='Phone number',
        widget=forms.TelInput(
            attrs={
                'autocomplete': 'tel',
                'placeholder': 'e.g. +250 7XX XXX XXX',
            }
        ),
    )
    country = forms.CharField(
        label='Country',
        required=False,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'country-name',
                'placeholder': 'Your country (optional)',
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'other_name',
            'email_address',
            'phone_number',
            'country',
            'password1',
            'password2',
        )
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

    def clean_email_address(self):
        email = self.cleaned_data['email_address'].lower()
        if User.objects.filter(email_address__iexact=email).exists():
            raise forms.ValidationError('An account already uses this email address.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Keep AbstractUser's inherited email field in sync for integrations
        # that still read it, while email_address remains the declared field.
        user.email = user.email_address
        user.country = self.cleaned_data.get('country') or None
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Allow a signed-in user to keep their public account details current."""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'other_name',
            'phone_number',
            'email_address',
        )
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'other_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'phone_number': forms.TelInput(attrs={'autocomplete': 'tel'}),
            'email_address': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def clean_email_address(self):
        email = self.cleaned_data['email_address'].lower()
        if User.objects.exclude(pk=self.instance.pk).filter(
            email_address__iexact=email
        ).exists():
            raise forms.ValidationError('An account already uses this email address.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.email_address
        if commit:
            user.save()
        return user


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ('language', 'font_size', 'font_family')


class ContentUploadForm(forms.Form):
    CONTENT_TYPES = (
        ('movie', 'Movie'),
        ('music', 'Music'),
        ('comedy', 'Comedy'),
        ('visual', 'Visual image'),
    )

    content_type = forms.ChoiceField(choices=CONTENT_TYPES, label='Content type')
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    content_file = forms.FileField(
        label='Content file',
        widget=forms.ClearableFileInput(attrs={'accept': 'video/*,image/*'}),
    )
    year_released = forms.IntegerField(label='Release year', min_value=1888, max_value=2100)
    category = forms.CharField(max_length=255, required=False)
    trailer_link = forms.URLField(required=False)
    production_studio = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('content_type') in {'movie', 'visual'} and not cleaned_data.get('category'):
            self.add_error('category', 'Choose a category for this content.')
        return cleaned_data


class AccountDeletionForm(forms.Form):
    username = forms.CharField(label='Username confirmation')
    password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.user.username:
            raise forms.ValidationError('Enter your username exactly to confirm deletion.')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError('Your current password is incorrect.')
        return password
