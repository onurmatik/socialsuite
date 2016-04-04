from django.contrib import admin
from django.http import HttpResponse
import networkx as nx
from social.tweets.models import Tweet, User, Hashtag, Symbol


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
    actions = ('tweet_graph', 'hashtag_user_graph')
    date_hierarchy = 'created_at'

    def tweet_graph(self, request, queryset):
        graph = Tweet.objects.tweet_graph(queryset)
        response = HttpResponse(
            '\n'.join(nx.generate_graphml(graph)),
            content_type='text/graphml'
        )
        response['Content-Disposition'] = 'attachment; filename=tweets.graphml'
        return response
    tweet_graph.short_description = 'Download tweet graph'

    def hashtag_user_graph(self, request, queryset):
        graph = Tweet.objects.hashtag_user_graph(queryset)
        response = HttpResponse(
            '\n'.join(nx.generate_graphml(graph)),
            content_type='text/graphml'
        )
        response['Content-Disposition'] = 'attachment; filename=hashtags-users.graphml'
        return response
    hashtag_user_graph.short_description = 'Download hashtag - user graph'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    pass
