from django.contrib import admin
from social.tokens.models import Application, AccessToken


class AccessTokenInline(admin.TabularInline):
    model = AccessToken


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'key', 'secret', 'status')
    list_editable = ('name', 'key', 'secret', 'status')
    inlines = (AccessTokenInline,)
