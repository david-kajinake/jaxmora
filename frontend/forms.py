from django import forms
from django.forms import formset_factory


class ContentUploadForm(forms.Form):
    """Single-item media upload form rendered by the JWT dashboard."""

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
    thumbnail = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
    )
    trailer_link = forms.URLField(required=False)
    production_studio = forms.CharField(max_length=255, required=False)


class SerieUploadForm(forms.Form):
    """Series metadata plus the first season that receives uploaded episodes."""

    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    year_released = forms.IntegerField(
        label='Series release year', min_value=1888, max_value=2100
    )
    category = forms.CharField(max_length=255)
    thumbnail = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
    )
    season_number = forms.IntegerField(min_value=1)
    season_name = forms.CharField(max_length=255, required=False)
    season_year = forms.IntegerField(
        label='Season release year', min_value=1888, max_value=2100
    )


class EpisodeUploadForm(forms.Form):
    """One episode in a series upload; used as a formset on the dashboard."""

    name = forms.CharField(max_length=255, label='Episode title')
    ref_number = forms.IntegerField(label='Episode number', min_value=1)
    video = forms.FileField(
        label='Episode video',
        widget=forms.ClearableFileInput(attrs={'accept': 'video/*'}),
    )


EpisodeUploadFormSet = formset_factory(
    EpisodeUploadForm,
    extra=1,
    min_num=1,
    validate_min=True,
    max_num=20,
    validate_max=True,
)
