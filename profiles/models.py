from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from tokens.models import OAuthToken
from twython import TwythonError, TwythonRateLimitError


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    screen_name = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    active = models.BooleanField(default=True)
    follow_history = models.BooleanField(default=getattr(settings, 'AUTO_FOLLOW_PROFILE_HISTORY', False))

    def __unicode__(self):
        return self.screen_name

    @property
    def followers_count(self):
        self._latest = getattr(self, '_latest', self.profile_set.last())  # cache
        return getattr(self._latest, 'followers_count', None)

    @property
    def friends_count(self):
        self._latest = getattr(self, '_latest', self.profile_set.last())  # cache
        return getattr(self._latest, 'friends_count', None)


class ProfileManager(models.Manager):
    def update_profiles(self):

        def chunks(l, n=100):  # 100 is the Twitter limit
            for i in xrange(0, len(l), n):
                yield l[i:i+n]

        rest_client = OAuthToken.objects.get_rest_client(access_level=OAuthToken.objects.READ)

        names = User.objects.filter(follow_history=True).filter(active=True).values_list('screen_name', flat=True)

        for chunk in chunks(names):
            try:
                profiles = rest_client.lookup_user(screen_name=','.join(chunk), entities=False)
            except TwythonRateLimitError:
                pass
            except TwythonError:
                pass
            else:
                for profile in profiles:
                    self.create(
                        user_id=profile['id'],
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


class Profile(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)

    screen_name = models.CharField(max_length=50)
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

    objects = ProfileManager()

    class Meta:
        ordering = ('-time',)
