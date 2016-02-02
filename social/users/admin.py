from django.contrib import admin
from social.users.models import User, ProfileHistory


class ProfileInline(admin.TabularInline):
    model = ProfileHistory


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'name', 'followers_count', 'friends_count', 'follow_history')
    list_editable = ('follow_history',)
    inlines = (ProfileInline,)


@admin.register(ProfileHistory)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('time', 'screen_name', 'name', 'followers_count', 'friends_count')
