from __future__ import unicode_literals

try:
    import queue
except ImportError:
    import Queue as queue

from django.db import models
from django.utils import timezone
from django.dispatch import Signal
from django.conf import settings
from twython import Twython, TwythonStreamer, TwythonError, TwythonRateLimitError
from tweets.models import Tweet
from tokens.models import OAuthToken
from logs.models import Log


tweet_received = Signal(providing_args=['stream', 'data'])


class Streamer(TwythonStreamer):
    def __init__(self, stream, **kwargs):
        self.stream = stream
        self.ignore_names = self.stream.ignore_names and stream.ignore_names.split(',')
        self.ignore_keywords = self.stream.ignore_keywords and stream.ignore_keywords.split(',')
        self.user_names = self.stream.screen_names and stream.screen_names.split(',')
        super(Streamer, self).__init__(**kwargs)

    def on_success(self, data):
        if 'text' in data:
            # check against filters
            ignore = False

            # users
            if self.stream.is_retweet is False and self.stream.is_reply is False:
                # we only care about those users' tweets
                if not data['user']['screen_name'] in self.user_names:
                    ignore = True

            # ignored users
            if data['user']['screen_name'] in self.ignore_names:
                ignore = True

            # ignored keywords and hashtags
            if not ignore:
                for keyword in self.ignore_keywords:
                    if keyword in data['text']:
                        ignore = True
                        break

            # minimum fav / rt counts
            if not ignore:
                if data['favorite_count'] < self.stream.min_favorite_count or \
                   data['retweet_count'] < self.stream.min_retweet_count:
                    ignore = True

            # existence of media
            if not ignore:
                if data['entities'].get('media'):
                    has_photo, has_video = False, False
                    for media in data['entities']['media']:
                        if media['type'] == 'photo':
                            has_photo = True
                        elif media['type'] == 'video':
                            has_video = True
                    if self.stream.has_photo != has_photo or self.stream.has_video != has_video:
                        ignore = True

            # existence of hashtags
            if not ignore:
                if not self.stream.has_hashtag is None:
                    has_hashtag = data['entities'].get('hashtags', False) and \
                                  len(data['entities']['hashtags']) > 0
                    if not has_hashtag == self.stream.has_hashtag:
                        ignore = True

            # existence of mentions
            if not ignore:
                if not self.stream.has_mention is None:
                    has_mention = data['entities'].get('user_mentions', False) and \
                                  len(data['entities']['user_mentions']) > 0
                    if not has_mention == self.stream.has_mention:
                        ignore = True

            # existence of symbols
            if not ignore:
                if not self.stream.has_symbol is None:
                    has_symbol = data['entities'].get('symbols', False) and \
                                 len(data['symbols']['user_mentions']) > 0
                    if not has_symbol == self.stream.has_symbol:
                        ignore = True

            # reply status
            if not ignore:
                if not self.stream.is_reply is None:
                    is_reply = not data.get('in_reply_to_status_id') is None
                    ignore = is_reply != self.stream.is_reply

            # retweet status
            is_retweet = None
            if not ignore:
                if not self.stream.is_retweet is None:
                    is_retweet = 'retweeted_status' in data
                    ignore = is_retweet != self.stream.is_retweet

            if is_retweet:
                try:
                    retweeted = Tweet.objects.get(id=data['retweeted_status']['id'])
                except Tweet.DoesNotExist:
                    # TODO: ids can be queued to be fetched by the rest client
                    pass
                else:
                    retweeted.retweet_count = data['retweeted_status']['retweet_count']
                    retweeted.favorite_count = data['retweeted_status']['favorite_count']
                    retweeted.save()

            if not ignore:
                if self.stream.save_tweets:
                    # create the tweet object and add it to the stream's tweet set
                    tweet = Tweet.objects.create_from_json(data)
                    self.stream.tweets.add(tweet)
                else:
                    # let another app handle the tweet
                    tweet_received.send(self.__class__, stream=self.stream, data=data)

        elif 'delete' in data:
            Tweet.objects.filter(id=data['delete']['status']['id']).update(deleted=timezone.now())

    def on_error(self, code, message):
        Log.objects.create(
            code=code,
            message=message,
            source='[stream-%s] %s' % (self.stream.id, self.stream.name)
        )


class StreamManager(models.Manager):
    def listen(self):
        for stream in self.all():
            stream.listen()


class Stream(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    screen_names = models.TextField(blank=True, null=True)
    user_ids = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    languages = models.TextField(blank=True, null=True)
    locations = models.TextField(blank=True, null=True)
    filter_level = models.CharField(max_length=1, default='n',
                                    choices=(('n', 'none'), ('l', 'low'), ('m', 'medium')))
    tweets = models.ManyToManyField(Tweet, blank=True)
    token = models.ForeignKey(OAuthToken, blank=True, null=True)

    # filters
    ignore_names = models.TextField(blank=True, null=True)
    ignore_keywords = models.TextField(blank=True, null=True)
    min_favorite_count = models.PositiveIntegerField(default=0)
    min_retweet_count = models.PositiveIntegerField(default=0)
    has_photo = models.NullBooleanField(default=None)
    has_video = models.NullBooleanField(default=None)
    has_hashtag = models.NullBooleanField(default=None)
    has_mention = models.NullBooleanField(default=None)
    has_symbol = models.NullBooleanField(default=None)
    is_retweet = models.NullBooleanField(default=None)
    is_reply = models.NullBooleanField(default=None)

    # Should we save the tweets or let another app handle them via signals
    save_tweets = models.BooleanField(default=getattr(settings, 'AUTO_SAVE_TWEETS', True))

    objects = StreamManager()

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if self.screen_names:
            if not self.id or Stream.objects.get(id=self.id).screen_names != self.screen_names:
                self.user_ids = self.fetch_user_ids()
        super(Stream, self).save(**kwargs)

    def fetch_user_ids(self):
        rest_client = OAuthToken.objects.get_rest_client(access_level=OAuthToken.objects.READ)
        user_ids = None
        try:
            result = rest_client.lookup_user(
                screen_name=self.screen_names,
                entities=False,
            )
        except TwythonRateLimitError as e:
            Log.objects.log_exception('[rest-%s] Rate limit error for %s' % (self.id, self.name), e)
        except TwythonError as e:
            Log.objects.log_exception('[rest-%s] Fetching user IDs for %s' % (self.id, self.name), e)
        else:
            user_ids = ','.join([user['id_str'] for user in result])
        return user_ids

    def get_params(self):
        params = {
            'filter_level': self.get_filter_level_display(),
        }
        if not self.user_ids in ['', None]:
            params['follow'] = self.user_ids
        if not self.keywords in ['', None]:
            params['track'] = self.keywords
        if not self.locations in ['', None]:
            params['locations'] = self.locations
        return params

    def get_stream_client(self):
        token = OAuthToken.objects.filter(application__status__lte=1).first()
        if not token:
            Log.objects.create(
                message='No token available',
                source='[stream-%s] Initializing %s' % (self.id, self.name),
                type=Log.ERROR,
            )
        else:
            return Streamer(
                app_key=token.application.key,
                app_secret=token.application.secret,
                oauth_token=token.token,
                oauth_token_secret=token.secret,
                stream=self,
            )

    def listen(self):
        stream_client = self.get_stream_client()
        Log.objects.create(
            message='Stream started',
            source='[stream-%s] Initialized %s' % (self.id, self.name),
            type=Log.INFO,
        )

        stream_client.statuses.filter(
            **self.get_params()
        )
