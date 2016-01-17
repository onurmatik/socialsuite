from django.contrib import admin
from tweets.models import Tweet, Hashtag, TweetHashtag, Symbol, Media, Link


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
        'tweet_id',
        'user',
        'text',
        'created_at',
        'favorite_count',
        'retweet_count',
        'has_geo',
        'is_reply',
        'is_retweet',
        'is_deleted',
        # m2m
        'media_count',
        'url_count',
        'mention_count',
        'hashtag_count',
    )
    list_display = FIELDS
    readonly_fields = FIELDS
    inlines = (
        MediaInline,
        HashtagInline,
        SymbolInline,
        LinkInline,
    )
    exclude = ('media', 'urls', 'mentions', 'hashtags', 'symbols')


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(TweetHashtag)
class TweetHashtagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'time')
