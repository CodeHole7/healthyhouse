from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OwnersDashboardConfig(AppConfig):
    label = 'owners_dashboard'
    name = 'dashboard.owners'
    verbose_name = _('Owners dashboard')
