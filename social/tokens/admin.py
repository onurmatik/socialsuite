from django.contrib import admin
from social.tokens.models import Application, OAuthToken


class OAuthTokenInline(admin.TabularInline):
    model = OAuthToken


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'key', 'secret', 'type', 'status')
    list_editable = ('name', 'key', 'secret', 'type', 'status')
    inlines = (OAuthTokenInline,)
