from __future__ import unicode_literals

from django.db import models


class Profile(models.Model):
    screen_name = models.CharField(max_length=50, unique=True, db_index=True)
    twitter_id = models.BigIntegerField(blank=True, null=True)  # nullable; may be fetched later from the API
    name = models.CharField(max_length=150, blank=True, null=True)
    verified = models.BooleanField(default=False)
    profile_image_url = models.URLField(blank=True, null=True)
    utc_offset = models.IntegerField(null=True, blank=True)
    time_zone = models.CharField(max_length=150, null=True, blank=True)
    geo_enabled = models.BooleanField(default=False)
    location = models.CharField(max_length=150, null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    friends_count = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.screen_name


class History(models.Model):
    profile = models.ForeignKey(Profile)
    time = models.DateTimeField()

    followers_count = models.PositiveIntegerField(default=0)
    friends_count = models.PositiveIntegerField(default=0)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=150, null=True, blank=True)

    name = models.CharField(max_length=150, blank=True, null=True)
    screen_name = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        verbose_name_plural = 'history'
