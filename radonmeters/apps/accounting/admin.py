from django.contrib import admin

from accounting.models import Accounting, AccountingLedgerItem


@admin.register(Accounting)
class AccountingAdmin(admin.ModelAdmin):
    model = Accounting

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(AccountingLedgerItem)
class AccountingLedgerItemAdmin(admin.ModelAdmin):
    readonly_fields = ['order', 'created']
    list_display = ['order', 'created']
