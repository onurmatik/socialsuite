from random import random
from datetime import datetime
from time import mktime
from redis import Redis
from twython import Twython, TwythonError, TwythonRateLimitError
from django.conf import settings
from django.core.management.base import NoArgsCommand


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

r = Redis(host='common.svkn4b.0001.euc1.cache.amazonaws.com')


def add_to_queue(user_id):
    user_id = str(user_id)
    following = r.lrange('following', 0, -1)
    if not following:
        following = twitter_client.get_friends_ids()['ids']
        r.rpush('following', *following)
        r.expire('following', 60 * 60 * 24)  # there may be manual follows/unfollows; expire daily
    if not user_id in following:  # not already following
        if len(r.lrange('follow', 0, -1)) > 20:  # trim the queue from the left
            r.ltrim('follow', -20, -1)
        if not user_id in r.lrange('follow', 0, -1):  # not already in the queue
            r.rpush('follow', user_id)


class Command(NoArgsCommand):
    def handle_noargs(self, *args, **options):
        now = int(mktime(datetime.now().timetuple()))  # float => int
        if now > int(r.get('retry_after') or '0'):  # redis returns str; cast to int
            user_id = r.rpop('follow')  # rpop => LIFO; lpop => FIFO
            try:
                twitter_client.create_friendship(user_id=user_id)
            except TwythonRateLimitError as e:
                r.set('retry_after', int(e.retry_after) + random() * 60 * 60)  # wait up to 1 extra hour
                r.rpush('follow', user_id)  # push it back to the queue
            except TwythonError as e:
                r.set('retry_after', now + 60 * 60 * 2)  # wait for 2 hours
                r.set('error', 'follow %s: %s @%s' % (e.error_code, e.msg, now))
                r.rpush('follow', user_id)  # push it back to the queue
            else:
                # we are following; prepend it to the following queue with lpush, because
                # the original queue is ordered with the most recent following first and
                # unfollow() consumes the queue starting from the oldest
                r.lpush('following', user_id)
