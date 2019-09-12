from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from address.models import MunicipalityRadonRisk


@admin.register(MunicipalityRadonRisk)
class MunicipalityRadonRiskAdmin(admin.ModelAdmin):
    search_fields = ('municipality',)
    list_filter = ('level',)
    list_display = ('municipality', 'avglevel', 'level')
    list_editable = ('avglevel', 'level')


from oscar.apps.address.admin import *