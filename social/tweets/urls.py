from django.conf.urls import url
from social.tweets.views import TweetListView, HashtagListView, HashtagDetailView


urlpatterns = [
    url(r'^$', TweetListView.as_view(), name='tweet_list'),
    url(r'^tag/$', HashtagListView.as_view(), name='hashtag_list'),
    url(r'^(?P<slug>\w+)/$', HashtagDetailView.as_view(), name='hashtag_detail'),
]
