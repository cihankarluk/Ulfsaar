from django.contrib import admin

from musicwire.transfer.models import TransferError


class TransferErrorModelAdmin(admin.ModelAdmin):
    list_display = 'source', 'end', 'type', 'user'
    search_fields = 'source', 'end', 'type', 'user__username'


admin.site.register(TransferError, TransferErrorModelAdmin)
