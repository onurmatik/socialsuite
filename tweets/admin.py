from django.contrib import admin
from tweets.models import Tweet, Hashtag, Symbol


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
        'is_deleted',
        'entity_count',
    )
    readonly_fields = (
        'text',
        'created_at',
        'favorite_count',
        'retweet_count',
        'has_geo',
        'is_reply',
        'is_retweet',
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


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    pass
