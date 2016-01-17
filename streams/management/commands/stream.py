from django.core.management.base import NoArgsCommand
from django.utils import timezone
from django.conf import settings
from twython import TwythonStreamer
from genelizleyici.vekiller.models import Vekil
from genelizleyici.tweets.models import Tweet, TwitterUser, Hashtag, TweetHashtag
from genelizleyici.streams.models import ErrorLog
from genelizleyici.utils import slugify
from genelizleyici.tweets.management.commands.follow import add_to_queue


def get_or_create_twitter_user(id, name, follow=True):
    user, created = TwitterUser.objects.get_or_create(username=name)
    if follow:
        add_to_queue(id)
    return user


class MeclisStreamer(TwythonStreamer):

    def on_success(self, data):
        if data.get('event') == 'user_update':
            avatar_url = data['source']['profile_image_url'].replace('_normal.', '.')
            Vekil.objects.filter(twitter_name=data['source']['screen_name']).update(avatar_url=avatar_url)

        elif 'retweeted_status' in data:
            try:
                retweeted = Tweet.objects.get(tweet_id=data['retweeted_status']['id_str'])
            except Tweet.DoesNotExist:
                pass
            else:
                retweeted.rt_count = data['retweeted_status']['retweet_count']
                retweeted.fav_count = data['retweeted_status']['favorite_count']
                retweeted.save()
                retweeted.retweets.add(*[
                    get_or_create_twitter_user(
                        id=data['user']['id'],
                        name=data['user']['screen_name'],
                        follow=False,
                    )
                ])

        elif 'text' in data:
            try:
                vekil = Vekil.objects.get(twitter_user=data['user']['screen_name'])
            except Vekil.DoesNotExist:
                vekil = None
            """
            # time is set to UTC instead of the current timezone? using timezone.now() instead
            time = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            time = timezone.make_aware(time, timezone.get_current_timezone())
            """
            now = timezone.now()
            followers = data['user']['followers_count']
            following = data['user']['friends_count']
            user = get_or_create_twitter_user(
                id=data['user']['id'],
                name=data['user']['screen_name'],
                follow=(not vekil) and followers > 500 and following / followers > 0.6,
            )
            tweet, created = Tweet.objects.get_or_create(
                tweet_id=data['id'],
                defaults={
                    'vekil': vekil,
                    'user': user,
                    'text': data['text'],
                    'time': now,
                    'lang': data['lang'],
                    'media': data['entities'].get('media') and data['entities']['media'][0]['media_url'] or None,
                    'media_type': data['entities'].get('media') and data['entities']['media'][0]['type'][0] or None,  # p: photo, v: video
                    'url': data['entities'].get('urls') and data['entities']['urls'][0]['expanded_url'] or None,
                    'fav_count': data['favorite_count'],
                    'rt_count': data['retweet_count'],
                    'reply_to': data['in_reply_to_status_id'],
                }
            )
            if created:
                # add mentions to m2m; MentionMap is not yet used
                tweet.mentions.add(*[
                    get_or_create_twitter_user(
                        id=m['id'],
                        name=m['screen_name'],
                        follow=False,
                    )
                    for m in data['entities']['user_mentions']
                ])

                # add hashtags to m2m intermediary table
                for h in data['entities']['hashtags']:
                    tag, created = Hashtag.objects.get_or_create(
                        slug=slugify(h['text']),
                        defaults={
                            'name': h['text'],
                        }
                    )
                    TweetHashtag.objects.create(
                        tag=tag,
                        vekil=tweet.vekil,
                        parti=tweet.vekil and tweet.vekil.parti,
                        sehir=tweet.vekil and tweet.vekil.sehir,
                        cinsiyet=tweet.vekil and tweet.vekil.cinsiyet,
                        tweet=tweet,
                        time=tweet.time,
                    )

                if data['in_reply_to_status_id']:
                    in_reply_to = Tweet.objects.filter(tweet_id=data['in_reply_to_status_id']).first()
                    if in_reply_to:
                        # no need to populate m2m; de-normalized way works fine
                        # in_reply_to.replies.add(tweet)
                        in_reply_to.reply_count += 1
                        in_reply_to.last_response = now
                        in_reply_to.save()

        elif 'delete' in data:
            Tweet.objects.filter(tweet_id=data['delete']['status']['id_str']).update(deleted=timezone.now())

        else:
            pass
            #print data

    def on_error(self, status_code, data):
        ErrorLog.objects.create(code=status_code, message=data)


stream = MeclisStreamer(
    settings.STREAM_TWITTER_KEY,
    settings.STREAM_TWITTER_SECRET,
    settings.STREAM_ACCESS_TOKEN,
    settings.STREAM_ACCESS_TOKEN_SECRET,
)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        ErrorLog.objects.create(
            code='000',
            message='Service restarted',
        )
        media_accounts = ['milliyet','cumhuriyetgzt','Aksam','AydinlikGazete','ulusalkanal','HDNER','tvahaber','radikal','DailySabah','Hurriyet','BugunTv','ulketv','ntv','Haber7','cnnturk','Sabah','todayszamancom','Vatan','tgrthabertv','trtturk','gazetesozcu','HaberturkTV','SHaberTV','yenisafak','postacomtr','tvnet','Ozgur_millet','turkiyegazetesi','Taraf_Medya','takvim','tgnewspaper','trthaber','zamancomtr','yurtgazetesi','evrenselgzt','DemokratHaber','artibirtv','hayat_tv','BirGun_Gazetesi','imc_televizyonu','yarinhaber','odatv','ozgurgundemweb','gercekgundemcom','sendika_org','baskahaber','jiyaninsesi','DikenComTr','P24Punto24','t24comtr','zetegazete','acikradyo','Vagustv','solhaberportali','bianet_org','Istanbul_Indy','otekilerpostasi','Revoltistanbul','AnarsiHaber','capul_tv','dokuz8haber','KameraSokak','140journos','yurtsuzhaber','etkinhaberajans','dhainternet','DicleHaberAjans','ANFTTURKCE','anadoluajansi','Cihan_Haber','ihacomtr','sputnik_TR','dw_turkce','AJTurk','bbcturkce','YuksekovaHaber','AGOSgazetesi','R_D_Kurdistan','TVsterkTV','jinhaberajans','Kazete_']
        vekil_accounts = list(Vekil.objects.exclude(twitter_id__isnull=True).values_list('twitter_id', flat=True))
        follow = ','.join(vekil_accounts)
        stream.statuses.filter(
            follow=follow,
            client_args={
                'verify': False,
            }
        )
