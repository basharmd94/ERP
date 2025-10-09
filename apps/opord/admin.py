from django.contrib import admin
from apps.opord.models import Opord

@admin.register(Opord)
class OpordAdmin(admin.ModelAdmin):
    list_display = ('xordernum', 'xdate', 'xcus', 'xstatusord', 'xsltype')
    search_fields = ('xordernum', 'xcus')
    list_filter = ('xdate', 'xstatusord', 'xsltype')
    ordering = ('-xdate',)
