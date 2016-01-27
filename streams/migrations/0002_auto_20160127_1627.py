# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='user_has_profile_image',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AddField(
            model_name='stream',
            name='user_is_geo_enabled',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AddField(
            model_name='stream',
            name='user_is_verified',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AddField(
            model_name='stream',
            name='user_min_follow_ratio',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stream',
            name='user_min_followers',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stream',
            name='user_min_following',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
