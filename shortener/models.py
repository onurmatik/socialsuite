from hexahexacontadecimal import hexahexacontadecimal_encode_int, hexahexacontadecimal_decode_int
from django.db import models
from django.core.cache import cache


class ShortURLManager(models.Manager):
    def get_or_create_short(self, url):
        short_url = cache.get(url)
        if not short_url:
            short, created = self.get_or_create(url=url)
            short_url = hexahexacontadecimal_encode_int(short.id)
            cache.set(url, short_url, None)
        return short_url

    def get_long(self, short):
        cache_key = 'short:%s' % short
        long_url = cache.get(cache_key)
        if not long_url:
            url_id = hexahexacontadecimal_decode_int(short)
            try:
                long_url = self.get(id=url_id).url
            except ShortURL.DoesNotExist:
                long_url = None
            else:
                cache.set(cache_key, long_url, None)
        return long_url


class ShortURL(models.Model):
    url = models.URLField()

    objects = ShortURLManager()

    def short(self):
        return hexahexacontadecimal_encode_int(self.id)
