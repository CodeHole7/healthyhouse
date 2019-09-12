from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class InstructionsDashboardConfig(AppConfig):
    label = 'instructions_dashboard'
    name = 'dashboard.instructions'
    verbose_name = _('Instructions dashboard')
