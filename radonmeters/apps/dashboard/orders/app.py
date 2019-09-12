from django.conf.urls import url
from oscar.apps.dashboard.orders.app import OrdersDashboardApplication as OrdersDashboardApplicationCore

from oscar.core.loading import get_class


class OrdersDashboardApplication(OrdersDashboardApplicationCore):
    order_create_view = get_class('dashboard.orders.views', 'OrderCreateView')

    def get_urls(self):
        urls = super().get_urls()
        urls = [
            url(r'^create/$',
                self.order_create_view.as_view(), name='order-create'),
        ] + urls
        return self.post_process_urls(urls)


application = OrdersDashboardApplication()
