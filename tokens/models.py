from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from twython import Twython


class Application(models.Model):
    OK, RESTRICTED, SUSPENDED = (0, 1, 2)

    name = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    type = models.CharField(max_length=1, choices=(
        ('l', 'Login'),
        ('s', 'Stream'),
        ('t', 'Tweet / Retweet'),
        ('f', 'Follow / Unfollow'),
    ), blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=(
        (OK, 'OK'),
        (RESTRICTED, 'Restricted write access'),
        (SUSPENDED, 'Suspended')
    ), default=0)


class OAuthTokenManager(models.Manager):
    READ, WRITE, MESSAGE = (1, 2, 3)

    def get_rest_client(self, access_level=WRITE):
        token = self.filter(application__status__lte=1).filter(access_level__gte=access_level).first()
        return token.get_rest_client()


class OAuthToken(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(User, blank=True, null=True)
    token = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    access_level = models.PositiveSmallIntegerField(choices=(
        (OAuthTokenManager.READ, 'Read only'),
        (OAuthTokenManager.WRITE, 'Read and Write'),
        (OAuthTokenManager.MESSAGE, 'Read, Write and Access direct messages'),
    ), default=OAuthTokenManager.WRITE)
    retry_after = models.DateTimeField(blank=True, null=True)

    objects = OAuthTokenManager()

    def __unicode__(self):
        return '%s - %s' % (self.application.name, self.get_access_level_display())

    def get_rest_client(self):
        return Twython(
            self.application.key,
            self.application.secret,
            self.token,
            self.secret,
        )

    def get_stream_client(self):
        return Twython(
            self.application.key,
            self.application.secret,
            self.token,
            self.secret,
        )


class RateLimitStatus(models.Model):
    token = models.ForeignKey(OAuthToken)
    time = models.DateTimeField(auto_now_add=True)
    resource = models.CharField(max_length=100)
    limit = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()
    reset = models.DateTimeField()
