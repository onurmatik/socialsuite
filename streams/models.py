from __future__ import unicode_literals

from django.db import models
from tweets.models import Tweet


class Stream(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    screen_names = models.TextField(blank=True, null=True)
    user_ids = models.TextField(blank=True, null=True, editable=False)
    keywords = models.TextField(blank=True, null=True)
    languages = models.TextField(blank=True, null=True)
    locations = models.TextField(blank=True, null=True)
    filter_level = models.CharField(max_length=1, blank=True, null=True,
                                    choices=(('l', 'low'), ('m', 'medium')))
    tweets = models.ManyToManyField(Tweet, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if self.screen_names:
            twitter_client = get_client()
            try:
                result = twitter_client.lookup_user(
                    user_id=self.screen_names,
                    entities=False,
                )
            except:
                pass
            else:
                self.user_ids = ','.join([user['id_str'] for user in result])
        super(Stream, self).save(**kwargs)
