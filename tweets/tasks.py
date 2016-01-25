from time import strftime, strptime
from celery import current_app
from genelizleyici.tweets.models import Tweet


@current_app.task
def create_tweet(status):
    Tweet.objects.create_from_json(status)
