from datetime import datetime
from django.utils import timezone
from email.utils import parsedate
from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify
from social.tokens.models import Application, READ
from twython import TwythonError, TwythonRateLimitError
from social.users.models import User


current_timezone = timezone.get_current_timezone()


def parse_datetime(string):
    if settings.USE_TZ:
        return datetime(*(parsedate(string)[:6]), tzinfo=current_timezone)
    else:
        return datetime(*(parsedate(string)[:6]))


class Hashtag(models.Model):
    name = models.CharField(max_length=140, unique=True, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if getattr(settings, 'AUTO_SLUGIFY_HASHTAG', False):
            self.slug = slugify(self.name)
        super(Hashtag, self).save(**kwargs)


class Link(models.Model):
    short_url = models.URLField(unique=True, db_index=True)
    expanded_url = models.URLField()

    def __unicode__(self):
        return self.expanded_url


class Media(models.Model):
    short_url = models.URLField(unique=True, db_index=True)
    expanded_url = models.URLField()
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


class TweetManager(models.Manager):
    def get_by_id(self, id, save=True):
        # TODO: handle exception and create using a task queue
        rest_client = Application.objects.get_rest_client(access_level=READ)
        result = rest_client.search(id=id)
        for data in result:
            self.create_from_json(data)

    def json_to_tweet(self, data):
        # Convert a json object received from the Twitter API to a Tweet object
        return Tweet(
            id=data['id'],
            text=data['text'],
            truncated=data['truncated'],
            lang=data.get('lang'),
            created_at=parse_datetime(data['created_at']),
            favorite_count=data['favorite_count'],
            retweet_count=data['retweet_count'],
            in_reply_to_status_id=data['in_reply_to_status_id'],
            in_reply_to_user_id=data['in_reply_to_user_id'],
            retweeted_status_id=data.get('retweeted_status') and data['retweeted_status']['id'],
            latitude=data.get('coordinates') and data['coordinates']['coordinates'][0],
            longitude=data.get('coordinates') and data['coordinates']['coordinates'][1],
        )

    def create_from_json(self, data):
        # Get or create a tweet object from the Twitter API response
        try:
            tweet = Tweet.objects.get(id=data['id'])
        except Tweet.DoesNotExist:
            tweet = self.json_to_tweet(data)
            tweet.user = User.objects.get_or_create(
                id=data['user']['id'],
                defaults={
                    'screen_name': data['user']['screen_name'],
                    'name': data['user']['name'],
                }
            )[0]
            tweet.save()
            tweet.mentions.add(*[
                User.objects.get_or_create(
                    id=mention['id'],
                    defaults={
                        'screen_name': mention['screen_name'],
                        'name': mention['name'],
                    }
                )[0] for mention in data['entities'].get('user_mentions', [])
            ])
            tweet.hashtags.add(*[
                Hashtag.objects.get_or_create(
                    name=hashtag['text']
                )[0] for hashtag in data['entities'].get('hashtags', [])
            ])
            tweet.symbols.add(*[
                Symbol.objects.get_or_create(
                    name=symbol['text']
                )[0] for symbol in data['entities'].get('symbols', [])
            ])
            tweet.media.add(*[
                Media.objects.get_or_create(
                    short_url=media['url'],
                    defaults={
                        'expanded_url': media['media_url'],
                        'type': media['type'][0],  # take the first letter of 'photo' or 'video'
                    }
                )[0] for media in data['entities'].get('media', [])
            ])
            tweet.urls.add(*[
                Link.objects.get_or_create(
                    short_url=url['url'],
                    defaults={
                        'expanded_url': url['expanded_url'],
                    }
                )[0] for url in data['entities'].get('urls', [])
            ])
        return tweet


class Tweet(models.Model):
    id = models.BigIntegerField(primary_key=True)
    text = models.CharField(max_length=250)
    truncated = models.BooleanField(default=False)
    lang = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(editable=False, db_index=True)
    favorite_count = models.PositiveIntegerField(default=0, db_index=True)
    retweet_count = models.PositiveIntegerField(default=0, db_index=True)
    in_reply_to_status_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    in_reply_to_user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    retweeted_status_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    latitude = models.FloatField(null=True, blank=True, db_index=True)
    longitude = models.FloatField(null=True, blank=True, db_index=True)

    user = models.ForeignKey(User)

    media = models.ManyToManyField(Media, blank=True)
    urls = models.ManyToManyField(Link, blank=True)
    symbols = models.ManyToManyField(Symbol, blank=True)
    mentions = models.ManyToManyField(User, blank=True, related_name='mentioned_tweets')
    hashtags = models.ManyToManyField(Hashtag, blank=True)

    replica_of = models.ForeignKey('self', blank=True, null=True)

    deleted = models.DateTimeField(blank=True, null=True)

    objects = TweetManager()

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
    def entity_count(self):
        counts = {
            'media': self.media.count(),
            'urls': self.urls.count(),
            '@': self.mentions.count(),
            '#': self.hashtags.count(),
            '$': self.symbols.count(),
        }
        return '; '.join(['%s %s' % (key, value) for key, value in counts.items() if value > 0])
