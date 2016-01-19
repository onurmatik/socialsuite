from django.contrib import admin
from tweets.models import Tweet


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
    FIELDS = (
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
    list_display = FIELDS
    readonly_fields = FIELDS
    inlines = (
        MediaInline,
        HashtagInline,
        SymbolInline,
        LinkInline,
    )
    exclude = ('tweets', 'media', 'urls', 'mentions', 'hashtags', 'symbols')
