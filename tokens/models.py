from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from twython import Twython


class Application(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    type = models.CharField(max_length=1, choices=(
        ('l', 'Login'),
        ('s', 'Stream'),
        ('t', 'Tweet / Retweet'),
        ('f', 'Follow / Unfollow'),
    ), blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=(
        (0, 'OK'),
        (1, 'Restricted write access'),
        (2, 'Suspended')
    ), default=0)


class OAuthToken(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(User)
    token = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    access_level = models.CharField(max_length=1, choices=(
        ('r', 'Read only'),
        ('w', 'Read and Write'),
        ('m', 'Read, Write and Access direct messages'),
    ), default='w')

    def __unicode__(self):
        return '%s - %s' % (self.application.name, self.user.username)

    def get_client(self):
        return Twython(
            self.application.key,
            self.application.secret,
            self.token,
            self.secret,
        )
