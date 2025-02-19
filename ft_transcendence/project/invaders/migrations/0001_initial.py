# Generated by Django 5.0.4 on 2024-05-24 19:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('high_score', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('game_over', models.BooleanField(default=False)),
                ('game', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='invaders_game', to='users.game')),
                ('player', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
