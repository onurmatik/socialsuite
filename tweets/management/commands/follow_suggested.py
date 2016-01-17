from django.db import models
from django.contrib.auth.models import User
import time
from django.conf import settings
from django.core.management.base import NoArgsCommand
from twython import Twython, TwythonError, TwythonRateLimitError


twitter_client = Twython(
    settings.UPDATER_TWITTER_KEY,
    settings.UPDATER_TWITTER_SECRET,
    settings.UPDATER_ACCESS_TOKEN,
    settings.UPDATER_ACCESS_TOKEN_SECRET,
#    settings.SOCIAL_AUTH_TWITTER_KEY,
#    settings.SOCIAL_AUTH_TWITTER_SECRET,
#    settings.TWITTER_ACCESS_TOKEN,
#    settings.TWITTER_ACCESS_TOKEN_SECRET,
)

#categories = twitter_client.get_user_suggestions()
#print categories

categories = [
    u'k\xf6\u015fe-yazarlar\u0131',
    u'yard\u0131m-kurulu\u015flar\u0131',
    u'haber',
    u'siyaset',
#    u'televizyon',
]

class Command(NoArgsCommand):
    def handle_noargs(self, *args, **options):
        for category in categories:
            suggestions = twitter_client.get_user_suggestions_by_slug(
                slug=category,
                lang='tr',
            )['users']
            for user in suggestions:
                print user['screen_name']
                try:
                    twitter_client.create_friendship(user_id=user['id'])
                except TwythonRateLimitError as e:
                    print 'sleeping %s' % e.retry_after
                    time.sleep(e.retry_after)
                except TwythonError as e:
                    print e.status, e.error_code
                    print e.error_msg
                    break
