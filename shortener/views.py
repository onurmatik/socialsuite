from django.views.generic import RedirectView
from genelizleyici.shortener.models import ShortURL


class RedirectShortView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return ShortURL.objects.get_long(kwargs['short'])
