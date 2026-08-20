from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Movie, Music, Comedy

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

admin.site.register([Movie, Music, Comedy])