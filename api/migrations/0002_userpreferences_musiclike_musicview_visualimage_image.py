# Generated manually to keep user display preferences and upload metrics together.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualimage',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='visual_images/'),
        ),
        migrations.CreateModel(
            name='MusicLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='music_likes', to=settings.AUTH_USER_MODEL)),
                ('music', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='api.music')),
            ],
        ),
        migrations.CreateModel(
            name='MusicView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('music', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='api.music')),
                ('viewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='music_views', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('sw', 'Kiswahili'), ('rw', 'Kinyarwanda'), ('fr', 'Francais')], default='en', max_length=2)),
                ('font_size', models.CharField(choices=[('very-small', 'Very small'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('very-large', 'Very large')], default='medium', max_length=12)),
                ('font_family', models.CharField(choices=[('dm-sans', 'DM Sans'), ('inter', 'Inter'), ('arial', 'Arial'), ('georgia', 'Georgia')], default='dm-sans', max_length=12)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
