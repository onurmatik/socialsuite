from django.http import JsonResponse, Http404
from django.views.decorators.cache import cache_page
from django.db.models import Count, F, ExpressionWrapper, Case, When
from social.users.models import ProfileHistory
from social.tokens.models import Application, READ
from social.tweets.models import Hashtag


@cache_page(60 * 5)  # cache for 5 mins; so if something goes wrong this won't hit the API repeatedly
def update_profile(request):
    if request.method == 'POST':
        profile_history = ProfileHistory.objects.filter(profile_image_url=request.POST.get('src')).first()
        if profile_history:
            rest_client = Application.objects.get_rest_client(access_level=READ)
            profile = rest_client.lookup_user(screen_name=profile_history.user.screen_name, entities=False)[0]
            ProfileHistory.create(
                user_id=profile['id'],
                screen_name=profile['screen_name'],
                name=profile['name'],
                description=profile['description'],
                verified=profile['verified'],
                profile_image_url=profile['profile_image_url'],
                lang=profile['lang'],
                utc_offset=profile['utc_offset'],
                time_zone=profile['time_zone'],
                geo_enabled=profile['geo_enabled'],
                location=profile['location'],
                followers_count=profile['followers_count'],
                friends_count=profile['friends_count'],
            )
            return JsonResponse({'src': profile['profile_image_url']})
    raise Http404


@cache_page(60 * 5)
def typeahead(request, **kwargs):
    qs = Hashtag.objects.filter(name__contains=kwargs['q'])
    qs = qs.values('tag__id', 'tag__name', 'tag__slug').annotate(
        AKP=Count(Case(When(parti='AKP', then='tag'))),
        CHP=Count(Case(When(parti='CHP', then='tag'))),
        MHP=Count(Case(When(parti='MHP', then='tag'))),
        HDP=Count(Case(When(parti='HDP', then='tag'))),
    )
    return qs.annotate(total=Count('tag__slug')).order_by('-total')
