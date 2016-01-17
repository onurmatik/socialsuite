from django.contrib import admin
from profiles.models import Profile, History


class HistoryInline(admin.TabularInline):
    model = History
    #readonly_fields = ('time', 'followers_count',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'name', 'followers_count', 'friends_count')
    inlines = (HistoryInline,)
