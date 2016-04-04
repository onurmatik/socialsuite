from datetime import datetime
import networkx as nx
from django.utils import timezone
from email.utils import parsedate
from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify
from social.tokens.models import Application, READ


current_timezone = timezone.get_current_timezone()


def parse_datetime(string):
    if settings.USE_TZ:
        return datetime(*(parsedate(string)[:6]), tzinfo=current_timezone)
    else:
        return datetime(*(parsedate(string)[:6]))


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    screen_name = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    def __unicode__(self):
        return self.screen_name


class Hashtag(models.Model):
    name = models.CharField(max_length=140, unique=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True, null=True)

    def save(self, **kwargs):
        if not self.slug and getattr(settings, 'AUTO_SLUGIFY_HASHTAG', False):
            self.slug = slugify(self.name)
        super(Hashtag, self).save(**kwargs)

    def __unicode__(self):
        return self.name


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
        return self.expanded_url


class Symbol(models.Model):
    name = models.CharField(max_length=140, unique=True)

    def __unicode__(self):
        return self.name


class Keyword(models.Model):
    term = models.CharField(max_length=50, unique=True)
    hashtag = models.CharField(max_length=140, unique=True, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True, null=True)
    ignore = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def hashtag_to_keyword(self):
        pass

    def keyword_to_hashtag(self):
        pass

    def save(self, **kwargs):
        if getattr(settings, 'AUTO_SLUGIFY_HASHTAG', False):
            self.slug = slugify(self.name)
        super(Keyword, self).save(**kwargs)


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

    def tweet_graph(self, qs):
        G = nx.Graph()
        for tweet in qs:
            G.add_node(
                tweet.id,
                label=tweet.text,
                type='tweet',
                lang=tweet.lang,
                created_at=tweet.created_at.strftime('%Y-%m-%d %H:%m'),
                favorite_count=tweet.favorite_count,
                retweet_count=tweet.retweet_count,
                is_reply=tweet.is_reply,
                is_retweet=tweet.is_retweet,
                is_deleted=tweet.is_deleted,
                has_geo=tweet.has_geo,
            )
            G.add_node(
                '@%s' % tweet.user.screen_name,
                type='user',
            )
            G.add_edge(
                tweet.id,
                '@%s' % tweet.user.screen_name,
                type='tweeted',
            )
            for hashtag in tweet.hashtags.all():
                G.add_node(
                    '#%s' % hashtag.name,
                    type='hashtag',
                )
                G.add_edge(
                    tweet.id,
                    '#%s' % hashtag.name,
                    type='tagged',
                )
            for mention in tweet.mentions.all():
                G.add_node(
                    '@%s' % mention.screen_name,
                    type='user',
                )
                G.add_edge(
                    tweet.id,
                    '@%s' % mention.screen_name,
                    type='mentioned',
                )
            for symbol in tweet.symbols.all():
                G.add_node(
                    '$%s' % symbol.name,
                    type='symbol',
                )
                G.add_edge(
                    tweet.id,
                    '$%s' % symbol.name,
                )
        return G

    def hashtag_user_graph(self, qs):
        G = nx.Graph()
        for tweet in qs:
            user = '@%s' % tweet.user.screen_name
            G.add_node(
                user,
                type='user',
            )
            for hashtag in tweet.hashtags.all():
                hashtag = '#%s' % hashtag.name
                G.add_node(
                    hashtag,
                    type='hashtag',
                )
                G.add_edge(
                    user,
                    hashtag,
                )
        return G


class Tweet(models.Model):
    id = models.BigIntegerField(primary_key=True)
    text = models.CharField(max_length=250)
    truncated = models.BooleanField(default=False)
    lang = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(db_index=True)
    favorite_count = models.PositiveIntegerField(default=0, db_index=True)
    retweet_count = models.PositiveIntegerField(default=0, db_index=True)
    in_reply_to_status_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    in_reply_to_user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    retweeted_status_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    latitude = models.FloatField(null=True, blank=True, db_index=True)
    longitude = models.FloatField(null=True, blank=True, db_index=True)

    user = models.ForeignKey(User)

    media = models.ManyToManyField(Media, through='TweetMedia', blank=True)
    urls = models.ManyToManyField(Link, through='TweetLink', blank=True)

    symbols = models.ManyToManyField(Symbol, through='TweetSymbol', blank=True)
    keywords = models.ManyToManyField(Keyword, through='TweetKeyword', blank=True)
    hashtags = models.ManyToManyField(Hashtag, through='TweetHashtag', blank=True)
    mentions = models.ManyToManyField(User, through='TweetMention', blank=True, related_name='mentioned_tweets')

    favorites = models.ManyToManyField(User, blank=True, related_name='favorited_tweets')
    retweets = models.ManyToManyField(User, blank=True, related_name='retweeted_tweets')

    repost_of = models.ForeignKey('self', blank=True, null=True)

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


# M2M through fields

class TweetHashtag(models.Model):
    tweet = models.ForeignKey(Tweet)
    hashtag = models.ForeignKey(Hashtag)
    time = models.DateTimeField(auto_now_add=True)
    lang = models.CharField(max_length=9, null=True, blank=True, db_index=True)


class TweetLink(models.Model):
    tweet = models.ForeignKey(Tweet)
    link = models.ForeignKey(Link)
    time = models.DateTimeField(auto_now_add=True)


class TweetMention(models.Model):
    tweet = models.ForeignKey(Tweet)
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)


class TweetMedia(models.Model):
    tweet = models.ForeignKey(Tweet)
    media = models.ForeignKey(Media)
    time = models.DateTimeField(auto_now_add=True)


class TweetSymbol(models.Model):
    tweet = models.ForeignKey(Tweet)
    symbol = models.ForeignKey(Symbol)
    time = models.DateTimeField(auto_now_add=True)


class TweetKeyword(models.Model):
    tweet = models.ForeignKey(Tweet)
    keyword = models.ForeignKey(Keyword)
    time = models.DateTimeField(auto_now_add=True)
    lang = models.CharField(max_length=9, null=True, blank=True, db_index=True)
