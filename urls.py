from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout
from django.utils.translation import ugettext_lazy as _


admin.site.site_header = _('Social Suite')


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tweets/', include('social.tweets.urls')),

    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
]
