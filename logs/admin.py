from django.contrib import admin
from logs.models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('code', 'message', 'time')
