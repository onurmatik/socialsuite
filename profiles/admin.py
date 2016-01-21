from django.contrib import admin
from profiles.models import User, Profile


class ProfileInline(admin.TabularInline):
    model = Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'name', 'followers_count', 'friends_count', 'follow_history')
    list_editable = ('follow_history',)
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('time', 'screen_name', 'name', 'followers_count', 'friends_count')
