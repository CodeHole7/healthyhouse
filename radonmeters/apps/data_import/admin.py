from django.contrib import admin

from data_import.models import ImportOrderObject


@admin.register(ImportOrderObject)
class ImportOrderObjectAdmin(admin.ModelAdmin):
    model = ImportOrderObject
    list_filter = ('created',)
    list_display = ('created',)
    readonly_fields = ('raw_data', 'cleaned_data', 'created', 'modified')

    def has_add_permission(self, request):
        return False
