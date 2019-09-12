from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DeliveriesDashboardConfig(AppConfig):
    label = 'deliveries_dashboard'
    name = 'dashboard.deliveries'
    verbose_name = _('Deliveries dashboard')
