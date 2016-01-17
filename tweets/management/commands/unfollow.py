from random import random
from datetime import datetime
from time import mktime
from redis import Redis
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

r = Redis(host='common.svkn4b.0001.euc1.cache.amazonaws.com')


class Command(NoArgsCommand):
    """
    Unfollows the oldest following that haven't followed back.
    """
    def handle_noargs(self, *args, **options):
        now = int(mktime(datetime.now().timetuple()))  # float => int
        if now > int(r.get('retry_after') or '0'):  # redis returns str; cast to int
            followers = r.lrange('followers', 0, -1)
            if not followers:
                followers = twitter_client.get_followers_ids()['ids']
                r.rpush('followers', *followers)
                r.expire('followers', 60 * 60)  # update hourly to include new followers
            # get the following list from the cache; do not attempt to created if is empty; follow() creates it
            # following list is ordered with the most recent following first
            # get the last user in the list (oldest following) that is not following back and unfollow
            unfollow = r.rpop('following')
            if unfollow:
                if unfollow not in followers:
                    try:
                        twitter_client.destroy_friendship(user_id=unfollow)
                    except TwythonRateLimitError as e:
                        r.rpush('following', unfollow)  # push it back to the queue or follow() can try to re-follow
                        r.set('retry_after', int(e.retry_after) + random() * 60 * 60)  # wait up to 1 extra hour
                    except TwythonError as e:
                        r.rpush('following', unfollow)  # push it back to the queue or follow() can try to re-follow
                        r.set('retry_after', now + 60 * 60 * 2)  # wait for 2 hours
                        r.set('error', 'unfollow %s: %s @%s' % (
                            e.error_code,
                            e.msg,
                            int(mktime(datetime.now().timetuple()))),
                        )
