# Generated by Django 2.2.7 on 2020-07-26 21:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('status', models.CharField(max_length=64)),
                ('remote_id', models.CharField(max_length=64)),
                ('content', models.CharField(max_length=64, null=True)),
                ('provider', models.CharField(choices=[('spotify', 'spotify'), ('youtube', 'youtube')], max_length=64)),
                ('is_transferred', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='account.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('artist', models.CharField(max_length=128, null=True)),
                ('album', models.CharField(max_length=128, null=True)),
                ('remote_id', models.CharField(max_length=155)),
                ('is_transferred', models.BooleanField(default=False)),
                ('provider', models.CharField(choices=[('spotify', 'spotify'), ('youtube', 'youtube')], max_length=64)),
                ('playlist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='music.Playlist')),
            ],
        ),
    ]
