from django.conf.urls import url
from oscar.apps.dashboard.vouchers.app import \
    VoucherDashboardApplication as CoreVoucherDashboardApplication

from oscar.core.loading import get_class


class VoucherDashboardApplication(CoreVoucherDashboardApplication):
    default_permissions = ['is_staff', ]

    voucher_bulk_create = get_class('vouchers.views', 'VoucherBulkCreateView')
    voucher_send_email = get_class('vouchers.views', 'VoucherSendEmailView')

    def get_urls(self):
        urls = super().get_urls()

        urls += [
            url(r'^bulk-create/$',
                self.voucher_bulk_create.as_view(),
                name='voucher-bulk-create'),
            url(r'^send-voucher/',
                self.voucher_send_email.as_view(),
                name='send-voucher')]

        return self.post_process_urls(urls)


application = VoucherDashboardApplication()
