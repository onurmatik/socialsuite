from django.conf.urls import url
from django.views.decorators.cache import cache_page
from genelizleyici.shortener.views import RedirectShortView


urlpatterns = [
    url(r'^(?P<short>.+)$', cache_page(60 * 60 * 24)(RedirectShortView.as_view()), name='redirect_short'),
]
