#encoding: UTF-8

from datetime import timedelta, datetime
from twython import Twython
from django.conf import settings
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.db.models import Count, Case, When, Max
from django.utils import timezone
from genelizleyici.tweets.models import Tweet, TweetHashtag


SHORT_URL_LENGTH = 23

twitter = Twython(
    settings.UPDATER_TWITTER_KEY,
    settings.UPDATER_TWITTER_SECRET,
    settings.UPDATER_ACCESS_TOKEN,
    settings.UPDATER_ACCESS_TOKEN_SECRET,
#    settings.SOCIAL_AUTH_TWITTER_KEY,
#    settings.SOCIAL_AUTH_TWITTER_SECRET,
#    settings.TWITTER_ACCESS_TOKEN,
#    settings.TWITTER_ACCESS_TOKEN_SECRET,
)


def short(msg):
    # shorten word by word
    while len(msg) > 137 - SHORT_URL_LENGTH:
        msg = msg[:msg.rfind(' ')]
    return msg


def top_tweet(party):
    # daily most popular tweet by party
    tweet = Tweet.objects.get_tweets(parti=party, tip='populer').first()
    if tweet:
        now = datetime.now()
        msg = u'#%s @%s: %s' % (
            tweet.vekil.parti,
            tweet.vekil.twitter_user,
            tweet.text,
        )
        url = 'http://genelizleyici.com%(uri)s?tip=populer&parti=%(party)s&baslangic=%(date)s&bitis=%(date)s' % {
            'uri': reverse('timeline'),
            'party': tweet.vekil.parti,
            'date': '%s-%s-%s' % (now.year, now.month, now.day),
        }
        #print u'%s %s' % (short(msg), url)
        twitter.update_status(status=u'%s … %s' % (short(msg), url))


def top_tag(party):
    # most popular hashtag of the day by party
    tag = Tweet.objects.get_tags(parti=party).first()
    if tag:
        msg = u'#%s @%s: %s' % (
            tweet.vekil.parti,
            tweet.vekil.twitter_user,
            tweet.text,
        )
        url = 'http://genelizleyici.com%s?tip=populer&mv=%s' % (reverse('timeline'), tweet.vekil.slug)

        print u'%s … %s' % (short(msg), url)
        #twitter.update_status(status=u'%s %s' % (short(msg), url))


def common_tag():
    # hashtag shared by more than 1 party
    qs = Tweet.objects.get_tags()
    qs = qs.exclude(Q(AKP=0, CHP=0, MHP=0) | Q(AKP=0, CHP=0, HDP=0) | Q(AKP=0, MHP=0, HDP=0) | Q(CHP=0, MHP=0, HDP=0))
    tag = qs.annotate(last=Max('time')).filter(last__lt=timezone.now()-timedelta(hours=3)).first()
    print tag
    if tag:
        parties = []
        if tag['AKP'] > 0: parties.append('#AKP')
        if tag['CHP'] > 0: parties.append('#CHP')
        if tag['MHP'] > 0: parties.append('#MHP')
        if tag['HDP'] > 0: parties.append('#HDP')
        msg = u'%s tartışıyor: #%s' % (
            ', '.join(parties),
            tag['tag__name'],
        )
        url = 'http://genelizleyici.com%s?konu=%s' % (reverse('timeline'), tag['tag__slug'])

        twitter.update_status(status=u'%s … %s' % (short(msg), url))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('type', type=str)
        parser.add_argument('party', nargs='?', type=str)

    def handle(self, *args, **options):
        if options['type'] == 'top_tweet':
            top_tweet(options['party'])
        elif options['type'] == 'common':
            common_tag()
