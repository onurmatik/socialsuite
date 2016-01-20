from django.contrib import admin
from tokens.models import Application, OAuthToken


class OAuthTokenInline(admin.TabularInline):
    model = OAuthToken


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'key', 'secret', 'type', 'status')
    list_editable = ('user', 'key', 'secret', 'type', 'status')
    inlines = (OAuthTokenInline,)
