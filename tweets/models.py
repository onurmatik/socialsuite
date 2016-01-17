#encoding: utf-8

import re
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from twython import Twython, TwythonError, TwythonRateLimitError


twitter_client = Twython(
    settings.TWITTER_KEY,
    settings.TWITTER_SECRET,
    settings.ACCESS_TOKEN,
    settings.ACCESS_TOKEN_SECRET,
)


class Hashtag(models.Model):
    name = models.CharField(max_length=140, unique=True)

    def __unicode__(self):
        return self.name


class Link(models.Model):
    short_url = models.URLField(unique=True, db_index=True)
    expanded_url = models.URLField()

    def __unicode__(self):
        return self.expanded_url


class Media(models.Model):
    url = models.URLField(unique=True, db_index=True)
    type = models.CharField(max_length=1, choices=(
        ('p', 'photo'),
        ('v', 'video'),
    ))

    def __unicode__(self):
        return self.url


class Symbol(models.Model):
    name = models.CharField(max_length=140, unique=True)

    def __unicode__(self):
        return self.name


class Tweet(models.Model):
    tweet_id = models.BigIntegerField()
    text = models.CharField(max_length=250)
    truncated = models.BooleanField(default=False)
    lang = models.CharField(max_length=9, null=True, blank=True)
    created_at = models.DateTimeField(db_index=True)
    favorite_count = models.PositiveIntegerField(default=0)
    retweet_count = models.PositiveIntegerField(default=0)
    in_reply_to_status_id = models.BigIntegerField(null=True, blank=True)
    in_reply_to_user_id = models.BigIntegerField(null=True, blank=True)
    retweeted_status_id = models.BigIntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True, default=None)
    longitude = models.FloatField(null=True, blank=True, default=None)

    user = models.ForeignKey(User, blank=True, default=None)
    user_screen_name = models.CharField(max_length=50)  # de-normalization; so tweet can be created before the user

    media = models.ManyToManyField(Media, blank=True)
    urls = models.ManyToManyField(Link, blank=True)
    symbols = models.ManyToManyField(Symbol, blank=True)

    mentions = models.ManyToManyField(User, blank=True, related_name='mentioned_tweets')

    hashtags = models.ManyToManyField(Hashtag, through='TweetHashtag', blank=True)

    deleted = models.DateTimeField(blank=True, null=True)

    @property
    def has_geo(self):
        return not self.latitude is None

    @property
    def is_reply(self):
        return not self.in_reply_to_status_id is None

    @property
    def is_retweet(self):
        return not self.retweeted_status_id is None

    @property
    def is_deleted(self):
        return not self.deleted is None

    @property
    def media_count(self):
        return self.media.count()

    @property
    def url_count(self):
        return self.urls.count()

    @property
    def mention_count(self):
        return self.mentions.count()

    @property
    def hashtag_count(self):
        return self.hashtags.count()


re_hashtag = re.compile(r'(\A|\W)#(\w{3,})', re.UNICODE)
re_username = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z_]+[A-Za-z0-9_]+)')


class TweetHashtag(models.Model):
    tag = models.ForeignKey(Hashtag)
    tweet = models.ForeignKey(Tweet)
    time = models.DateTimeField(auto_now_add=True, db_index=True)
