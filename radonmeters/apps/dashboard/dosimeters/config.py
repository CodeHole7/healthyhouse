from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DosimetersDashboardConfig(AppConfig):
    label = 'dosimeters_dashboard'
    name = 'dashboard.dosimeters'
    verbose_name = _('Dosimeters dashboard')
