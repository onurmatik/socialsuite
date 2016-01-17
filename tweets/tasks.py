from time import strftime, strptime
from celery import current_app
from genelizleyici.tweets.models import Tweet


@current_app.task
def create_tweet(status):
    tweet, created = Tweet.objects.get_or_create(
        tweet_id=status['id'],
        defaults={
            'username': status['user'],
            'text': status['text'],
            'time': strftime('%Y-%m-%d %H:%M:%S', strptime(status['created_at'],'%a %b %d %H:%M:%S +0000 %Y')),
            'lang': status['lang'],
            'media': status['entities'].get('media') and status['entities']['media'][0]['media_url'] or None,
            'media_type': status['entities'].get('media') and status['entities']['media'][0]['type'][0] or None,  # p: photo, v: video
            'url': status['entities'].get('urls') and status['entities']['urls'][0]['expanded_url'] or None,
            'fav_count': status['favorite_count'],
            'rt_count': status['retweet_count'],
            'reply_to': status['in_reply_to_status_id'],
        }
    )
    if created:
        tweet.mentions.add(*status['entities']['user_mentions'])
        tweet.hashtags.add(*status['entities']['hashtags'])
