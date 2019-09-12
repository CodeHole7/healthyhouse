from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VouchersDashboardConfig(AppConfig):
    label = 'voucher_dashboard'
    name = 'dashboard.vouchers'
    verbose_name = _('Vouchers dashboard')
