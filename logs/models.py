from __future__ import unicode_literals

from django.db import models


class Log(models.Model):
    code = models.CharField(max_length=5)
    message = models.TextField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
