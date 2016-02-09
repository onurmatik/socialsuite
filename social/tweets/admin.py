from django.contrib import admin
from social.tweets.models import Tweet, Hashtag, Symbol
import unicodecsv


class MediaInline(admin.TabularInline):
    model = Tweet.media.through
    readonly_fields = ('media',)
    max_num = 0


class HashtagInline(admin.TabularInline):
    model = Tweet.hashtags.through
    readonly_fields = ('hashtag',)
    max_num = 0


class SymbolInline(admin.TabularInline):
    model = Tweet.symbols.through
    readonly_fields = ('symbol',)
    max_num = 0


class LinkInline(admin.TabularInline):
    model = Tweet.urls.through
    readonly_fields = ('link',)
    max_num = 0


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'text',
        'created_at',
        'is_reply',
        'is_retweet',
        'lang',
        'retweet_count',
        'favorite_count',
        'is_deleted',
        'entity_count',
    )
    inlines = (
        MediaInline,
        HashtagInline,
        SymbolInline,
        LinkInline,
    )
    exclude = ('media', 'urls', 'mentions', 'hashtags', 'symbols')
    actions = ('export_to_graphml', 'export_tweets', 'export_hashtags')
    date_hierarchy = 'created_at'

    def export_to_graphml(self, request, queryset):
        import networkx as nx
        from django.http import HttpResponse
        graph = Tweet.objects.to_graph(queryset)
        response = HttpResponse(
            '\n'.join(nx.generate_graphml(graph)),
            content_type='text/graphml'
        )
        response['Content-Disposition'] = 'attachment; filename=tweets.graphml'
        return response

    def export_tweets(self, request, queryset):
        """
        user | time | tweet | lang | has_hashtag | has_media | has_link
        """
        f = open('tweets.csv', 'wb')
        writer = unicodecsv.writer(f, encoding='utf-8')
        writer.writerow((
            'user',
            'time',
            'tweet',
            'lang',
            'has_hashtag',
            'has_media',
            'has_link',
        ))
        for tweet in queryset:
            writer.writerow((
                tweet.user.screen_name,
                tweet.created_at,
                tweet.text.replace('\n', ' '),
                tweet.lang,
                tweet.hashtags.count() > 0,
                tweet.media.count() > 0,
                tweet.urls.count() > 0,
            ))
        f.close()

    def export_hashtags(self, request, queryset):
        """
        user | time | hashtag | lang | has_media | has_link
        """
        f = open('hashtags.csv', 'wb')
        writer = unicodecsv.writer(f, encoding='utf-8')
        writer.writerow((
            'user',
            'time',
            'hashtag',
            'lang',
            'has_media',
            'has_link',
        ))
        for tweet in queryset:
            for hashtag in tweet.hashtags.all():
                writer.writerow((
                    tweet.user.screen_name,
                    tweet.created_at,
                    hashtag.name,
                    tweet.lang,
                    tweet.media.count() > 0,
                    tweet.urls.count() > 0,
                ))
        f.close()


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    pass
