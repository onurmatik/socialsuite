from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from twython import Twython
from social.tweets.models import Tweet, Hashtag


class TweetListView(ListView):
    model = Tweet
    paginate_by = 20

    def get_queryset(self):
        qs = super(TweetListView, self).get_queryset()
        type = getattr(self, 'type', None)
        if type:
            if type == 'popular':
                qs = qs.filter(deleted__isnull=True).order_by('-rank')
            elif type == 'deleted':
                qs = qs.exclude(deleted__isnull=True).annotate(
                    delta=ExpressionWrapper(
                        F('deleted') - F('created_at'), output_field=models.DurationField()
                    )
                ).filter(delta__gt=timedelta(minutes=5)).order_by('-deleted')  # sqlite3'te bu filtre calismiyor; empty qs donuyor
            else:
                qs = qs.filter(deleted__isnull=True).order_by('-created_at')
        return qs

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            tweets = []
            for tweet in self.get_queryset():
                # is reply?
                reply_to_user = None
                reply_to_html = None
                if tweet.in_reply_to_status_id:
                    try:
                        reply_to = Tweet.objects.get(tweet_id=tweet.in_reply_to_status_id)
                    except Tweet.DoesNotExist:
                        pass
                    else:
                        reply_to_user = reply_to.user.username
                        reply_to_html = reply_to.html

                social_user = tweet.user
                social_profile = social_user.current_profile
                profile = getattr(tweet.user, 'profile', None)
                media = tweet.media.all().first()
                tweets.append({
                    'id': tweet.tweet_id,
                    'profile_name': social_profile and social_profile.name or social_user.name,
                    'profile_party': profile and profile.get_party_display() or 'secmen',
                    'profile_image_url': social_profile.profile_image_url,
                    'profile_title': profile and profile.title or '-',
                    'tweet_html': tweet.html,
                    'tweet_time': naturaltime(tweet.created_at),
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'reply_count': tweet.reply_count,
                    'tweet_deleted': tweet.deleted_timedelta,
                    'tweet_media': media,
                    'tweet_video': media.type == 'v' and media,
                    'tweet_url': tweet.url,
                    'slug': profile.slug,
                    'reply_to_user': reply_to_user,
                    'reply_to_html': reply_to_html
                })
            return JsonResponse(
                tweets,
                safe=False
            )
        else:
            return super(TweetListView, self).render_to_response(context, **kwargs)


class HashtagListView(ListView):
    model = Hashtag
    paginate_by = 10

    def get_queryset(self):
        qs = super(HashtagListView, self).get_queryset()
        date = getattr(self, 'date', None)
        if date:
            qs = qs.filter(time__date=date)
        return qs

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            hashtags = []
            for hashtag in self.get_queryset():
                hashtags.append({
                    'tag': hashtag.name,
                    'slug': hashtag.slug,
                })
            return JsonResponse(
                hashtags,
                safe=False
            )
        else:
            return super(HashtagListView, self).render_to_response(context, **kwargs)


class HashtagDetailView(DetailView):
    model = Hashtag

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            hashtag = self.get_object()
            return JsonResponse(
                {
                    'name': hashtag.name,
                    'stats': hashtag.stats,
                    'tarih': {
                        'ilk': naturalday(date_range['first']),
                        'son': date_range['first'].date() != date_range['last'].date() and naturalday(date_range['last']) or None,
                    },
                    'konular': [
                        {
                            'konu': t['tag__name'],
                        } for t in hashtag.related_tags
                    ],
                }, safe=False
            )
        else:
            return super(HashtagDetailView, self).render_to_response(context, **kwargs)
