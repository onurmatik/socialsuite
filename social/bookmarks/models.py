from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from social.tweets.models import Tweet


class Tag(models.Model):
    name = models.CharField(max_length=50)


class Bookmark(models.Model):
    tweet = models.ForeignKey(Tweet)
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, blank=True)
    time = models.DateTimeField(auto_now_add=True)
