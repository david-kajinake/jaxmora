from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Comedy,
    Episode,
    Movie,
    Music,
    Season,
    Serie,
    User,
    UserPreferences,
    VisualImage,
)


class UserPreferencesInline(admin.StackedInline):
    model = UserPreferences
    extra = 0
    max_num = 1
    can_delete = False

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username','first_name','other_name','email_address','phone_number' ,'country')
    readonly_fields = ('date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('JAXMORA profile', {'fields': ('other_name', 'email_address', 'phone_number', 'country')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('JAXMORA profile', {'fields': ('first_name', 'other_name', 'email_address', 'phone_number', 'country')}),
    )
    inlines = (UserPreferencesInline,)


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ('ref_number', 'name', 'year_released', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    show_change_link = True


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0
    fields = ('ref_number', 'name', 'video', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'year_released', 'uploaded_at')
    list_filter = ('category', 'year_released')
    search_fields = ('title', 'owner__username')
    readonly_fields = ('uploaded_at', 'updated_at')
    inlines = (SeasonInline,)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('serie', 'ref_number', 'name', 'year_released', 'uploaded_at')
    list_filter = ('year_released',)
    search_fields = ('serie__title', 'name')
    readonly_fields = ('uploaded_at',)
    inlines = (EpisodeInline,)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'ref_number', 'uploaded_at')
    list_filter = ('season__serie',)
    search_fields = ('name', 'season__serie__title')
    readonly_fields = ('uploaded_at',)

admin.site.register([Movie, Music, Comedy, VisualImage, UserPreferences])
