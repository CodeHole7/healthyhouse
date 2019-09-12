from django.contrib import admin
from django.utils.html import format_html

from providers.stripe_app.models import StripeCharge


class StripeAdminMixin:

    @staticmethod
    def stripe_dashboard_url(obj):
        return format_html(
            '<a href="{}" target="_blank">Open in Stripe</a>',
            obj.stripe_dashboard_url)

    def get_list_display(self, request):
        return (
            *super().get_list_display(request),
            'stripe_dashboard_url')


@admin.register(StripeCharge)
class StripeChargeAdmin(StripeAdminMixin, admin.ModelAdmin):
    model = StripeCharge
    readonly_fields = ('id', 'stripe_id')
    list_filter = ('created', 'modified')

    list_display = ('id', 'stripe_id', 'order', 'created', 'modified')
    search_fields = ('id', 'stripe_id')
