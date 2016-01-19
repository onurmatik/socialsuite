from django.contrib import admin
from logs.models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('source', 'code', 'message', 'time', 'retry_after')
