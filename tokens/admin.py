from django.contrib import admin
from tokens.models import Application, OAuthToken


class OAuthTokenInline(admin.TabularInline):
    model = OAuthToken


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'key', 'secret', 'type', 'status')
    list_editable = ('user', 'name', 'key', 'secret', 'type', 'status')
    inlines = (OAuthTokenInline,)
