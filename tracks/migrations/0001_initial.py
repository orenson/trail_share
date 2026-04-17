import uuid
import tracks.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_private', models.BooleanField(default=False)),
                ('cover_color', models.CharField(default='#2D6A4F', max_length=7)),
                ('invite_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_groups', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='joined_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('gpx_file', models.FileField(upload_to=tracks.models.gpx_upload_path)),
                ('activity_type', models.CharField(choices=[('hiking', 'Hiking'), ('running', 'Running'), ('cycling', 'Cycling'), ('mtb', 'Mountain Biking'), ('skiing', 'Skiing'), ('other', 'Other')], default='hiking', max_length=20)),
                ('distance_km', models.FloatField(blank=True, null=True)),
                ('elevation_gain_m', models.FloatField(blank=True, null=True)),
                ('elevation_loss_m', models.FloatField(blank=True, null=True)),
                ('max_elevation_m', models.FloatField(blank=True, null=True)),
                ('duration_seconds', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='tracks.group')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
