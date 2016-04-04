from django.contrib import admin
from social.profilehistory.models import ProfileHistory


class ProfileInline(admin.TabularInline):
    model = ProfileHistory


@admin.register(ProfileHistory)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('time', 'screen_name', 'name', 'followers_count', 'friends_count')
