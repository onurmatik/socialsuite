from django.contrib import admin
from tweets.models import Tweet, Hashtag, Mention, Symbol


class MediaInline(admin.TabularInline):
    model = Tweet.media.through


class HashtagInline(admin.TabularInline):
    model = Tweet.hashtags.through


class SymbolInline(admin.TabularInline):
    model = Tweet.symbols.through


class LinkInline(admin.TabularInline):
    model = Tweet.urls.through


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = (
        'user_screen_name',
        'text',
        'created_at',
        'is_reply',
        'is_retweet',
        'lang',
        'is_deleted',
        'entity_count',
    )
    readonly_fields = (
        'user_screen_name',
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
    exclude = ('tweets', 'media', 'urls', 'mentions', 'hashtags', 'symbols')


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    pass


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    pass
