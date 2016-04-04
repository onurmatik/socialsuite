from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from birdy import twitter


OK, RESTRICTED, SUSPENDED = (0, 1, 2)
READ, WRITE, MESSAGE = (1, 2, 3)


class ApplicationManager(models.Manager):
    def get_rest_client(self, access_level=WRITE):
        token = self.filter(application__status__lte=1).filter(access_level__gte=access_level).first()
        return token.get_rest_client()


class Application(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    access_level = models.PositiveSmallIntegerField(choices=(
        (READ, 'Read only'),
        (WRITE, 'Read and Write'),
        (MESSAGE, 'Read, Write and Access direct messages'),
    ), default=WRITE)
    status = models.PositiveSmallIntegerField(choices=(
        (OK, 'OK'),
        (RESTRICTED, 'Restricted write access'),
        (SUSPENDED, 'Suspended'),
    ), default=OK)

    objects = ApplicationManager()


class AccessToken(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(User, blank=True, null=True)
    token = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    retry_after = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.application.name

    def get_rest_client(self):
        return twitter.UserClient(
            self.application.key,
            self.application.secret,
            self.token,
            self.secret,
        )

    def get_stream_client(self):
        return twitter.StreamClient(
            self.application.key,
            self.application.secret,
            self.token,
            self.secret,
        )


class RateLimitStatus(models.Model):
    token = models.ForeignKey(AccessToken)
    time = models.DateTimeField(auto_now_add=True)
    resource = models.CharField(max_length=100)
    limit = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()
    reset = models.DateTimeField()
