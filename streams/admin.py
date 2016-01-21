from django.contrib import admin
from streams.models import Stream


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'filter_level')
    list_editable = ('name', 'filter_level', )
    readonly_fields = ('user_ids',)
    exclude = ('tweets',)
