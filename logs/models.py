from __future__ import unicode_literals

from django.db import models
from datetime import datetime


class LogManager(models.Manager):
    def log_exception(self, source, e):
        self.create(
            code=e.error_code,
            message=e.msg,
            retry_after=e.retry_after and datetime.fromtimestamp(int(e.retry_after)),
            source=source,
            type='e',
        )


class Log(models.Model):
    source = models.CharField(max_length=150)
    code = models.CharField(max_length=5, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    retry_after = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=(
        ('i', 'info'),
        ('w', 'warning'),
        ('e', 'error'),
    ), default='i')
    time = models.DateTimeField(auto_now_add=True)

    objects = LogManager()

    def __unicode__(self):
        return '[%s] %s: %s' % (self.source, self.code, self.message)
