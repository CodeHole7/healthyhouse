from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DefaultProductsDashboardConfig(AppConfig):
    label = 'default_products_dashboard'
    name = 'dashboard.default_products'
    verbose_name = _('Default products dashboard')
