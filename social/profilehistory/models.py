from __future__ import unicode_literals

from django.db import models
from social.tokens.models import Application, READ


class ProfileHistoryManager(models.Manager):
    def update_history(self, names):

        def chunks(l, n=100):  # 100 is the Twitter limit
            for i in xrange(0, len(l), n):
                yield l[i:i+n]

        rest_client = Application.objects.get_rest_client(access_level=READ)

        for chunk in chunks(names):
            try:
                profiles = rest_client.lookup_user(screen_name=','.join(chunk), entities=False)
            except:
                pass
            else:
                for profile in profiles:
                    self.create(
                        screen_name=profile['screen_name'],
                        name=profile['name'],
                        description=profile['description'],
                        verified=profile['verified'],
                        profile_image_url=profile['profile_image_url'],
                        lang=profile['lang'],
                        utc_offset=profile['utc_offset'],
                        time_zone=profile['time_zone'],
                        geo_enabled=profile['geo_enabled'],
                        location=profile['location'],
                        followers_count=profile['followers_count'],
                        friends_count=profile['friends_count'],
                    )


class ProfileHistory(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    screen_name = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    profile_image_url = models.URLField(blank=True, null=True)
    lang = models.CharField(max_length=9, null=True, blank=True)
    utc_offset = models.IntegerField(null=True, blank=True)
    time_zone = models.CharField(max_length=150, null=True, blank=True)
    geo_enabled = models.BooleanField(default=False)
    location = models.CharField(max_length=150, null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    friends_count = models.PositiveIntegerField(default=0)

    objects = ProfileHistoryManager()

    class Meta:
        ordering = ('-time',)
        verbose_name_plural = 'Profile history'
