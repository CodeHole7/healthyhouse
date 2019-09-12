from django.contrib import admin

from catalogue.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']
