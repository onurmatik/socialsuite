from django.db.models import Count, Case, When
from django.http import JsonResponse, Http404
from django.template import defaultfilters
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime, intword, naturalday
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from twython import Twython
from genelizleyici.utils import slugify
from genelizleyici.vekiller.models import Vekil
from genelizleyici.tweets.models import Tweet, Hashtag


@cache_page(60 * 15, key_prefix="api:tags")
def tags(request):
    kwargs = {k: v for k, v in request.GET.items()}
    limit = request.GET.get('limit', 10)
    tweet_hashtags = Tweet.objects.get_tags(**kwargs)[:limit]
    result = []
    for item in tweet_hashtags:
        result.append({
            'tag': item['tag__name'],
            'slug': slugify(item['tag__name']),
            'AKP': item['AKP'],
            'CHP': item['CHP'],
            'MHP': item['MHP'],
            'HDP': item['HDP'],
        })
    return JsonResponse(result, safe=False)


@cache_page(60 * 15, key_prefix="api:tags")
def tag_detail(request):
    slug = slugify(request.GET.get('konu', ''))
    try:
        tag = Hashtag.objects.get(slug=slug)
    except Tweet.DoesNotExist:
        return Http404
    date_range = tag.date_range
    result = {
        'konu': tag.name,
        'stats': tag.stats,
        'tarih': {
            'ilk': naturalday(date_range['first']),
            'son': date_range['first'].date() != date_range['last'].date() and naturalday(date_range['last']) or None,
        },
        'konular': [
            {
                'konu': t['tag__name'],
            } for t in tag.related_tags
        ],
    }
    return JsonResponse(result, safe=False)


def tweets(request):
    kwargs = {k: v for k, v in request.GET.items()}
    qs = Tweet.objects.get_tweets(**kwargs)
    p = Paginator(qs, 20)
    try:
        page = p.page(request.GET.get('sayfa', 1))
    except:
        return JsonResponse([], safe=False)
    tweets = []
    for tweet in page.object_list:
        # reply
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
        vekil = tweet.vekil
        tweets.append({
            'id': tweet.tweet_id,
            'vekil_isim': vekil.isim,
            'vekil_parti': vekil.parti,
            'vekil_avatar_url': vekil.avatar_url,
            'vekil_sehir': vekil.get_sehir_display(),
            'vekil_donem': vekil.donem,
            'tweet_html': tweet.html,
            'tweet_time': naturaltime(tweet.created_at),
            'retweet_count': tweet.retweet_count,
            'favorite_count': tweet.favorite_count,
            'reply_count': tweet.reply_count,
            'tweet_deleted': tweet.deleted_timedelta,
            'tweet_media': tweet.media,
            'tweet_video': tweet.media_type == 'v' and tweet.media,
            'tweet_url': tweet.url,
            'slug': vekil.slug,
            'reply_to_user': reply_to_user,
            'reply_to_html': reply_to_html
        })
    return JsonResponse(tweets, safe=False)


def replies(request):
    tweet_id = request.GET.get('id')
    qs = Tweet.objects.filter(in_reply_to_status_id=tweet_id).filter(deleted__isnull=True)
    p = Paginator(qs, 5)
    try:
        page = p.page(request.GET.get('page', 1))
    except:
        return JsonResponse([], safe=False)
    return JsonResponse(
        [{
            'user': tweet.user.username,
            'tweet': tweet.mentions_stripped,
        } for tweet in page.object_list],
        safe=False,
    )


def mp_list(request):
    limit = request.GET.get('limit', 10)
    q = request.GET.get('q', '')
    mps = Vekil.objects.filter(isim__icontains=q)[:limit]
    result = []
    for mp in mps:
        result.append({
            'name': mp.isim,
            'party': mp.parti,
            'city': mp.get_sehir_display(),
            'slug': mp.slug,
        })
    return JsonResponse(result, safe=False)


def mp_detail(request):
    slug = slugify(request.GET.get('mv', ''))
    try:
        mp = Vekil.objects.get(slug=slug)
    except Vekil.DoesNotExist:
        return Http404
    result = {
        'isim': mp.isim,
        'parti': mp.parti,
        'sehir': mp.get_sehir_display(),
        'donem': mp.donem,
        'ozet': mp.ozet and defaultfilters.linebreaks(defaultfilters.urlize(mp.ozet)),
        'takipci_sayi': intword(mp.followers_count),
        'takipci_sira': mp.followers_rank,
        'paylasim_sayi': intword(mp.statuses_total),
        'paylasim_sira': mp.statuses_rank,
        'fav_sayi': intword(mp.fav_total),
        'fav_sira': mp.fav_rank,
        'rt_sayi': intword(mp.rt_total),
        'rt_sira': mp.rt_rank,
        'tags': [{'tag': h.name} for h in Hashtag.objects.filter(tweet__vekil=mp).distinct()],
    }
    return JsonResponse(result, safe=False)


# POST operations

def authenticate(user):
    social = user.social_auth.get(provider='twitter')
    api = Twython(
        settings.SOCIAL_AUTH_TWITTER_KEY,
        settings.SOCIAL_AUTH_TWITTER_SECRET,
        social.extra_data['access_token']['oauth_token'],
        social.extra_data['access_token']['oauth_token_secret'],
    )
    return api


@login_required
def reply(request):
    if request.method == 'POST':
        params = request.POST
        mp = Vekil.objects.get(slug=slugify(params['slug']))
        status = '@%s %s' % (mp.twitter_user, params['text'])
        api = authenticate(request.user)
        response = api.update_status(
            status=status,
            in_reply_to_status_id=params['reply_to'],
        )
        return JsonResponse(response)


@login_required
def fav(request):
    if request.method == 'POST':
        params = request.POST
        api = authenticate(request.user)
        if params.get('unfav'):
            f = api.destroy_favorite
        else:
            f = api.create_favorite
        response = f(
            id=params['id'],
            include_entities=False,
        )
        return JsonResponse({
            'favorited': response['favorited'],
            'favorite_count': response['favorite_count'],
        })


@login_required
def rt(request):
    if request.method == 'POST':
        params = request.POST
        api = authenticate(request.user)
        response = api.retweet(
            id=params['id'],
            trim_user=True,
        )
        return JsonResponse({
            'retweeted': response['retweeted'],
            'retweet_count': response['retweet_count'],
        })
