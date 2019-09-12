from django.conf.urls import url

from oscar.apps.dashboard.app import \
    DashboardApplication as CoreDashboardApplication
from oscar.core.loading import get_class


class DashboardApplication(CoreDashboardApplication):
    deliveries_app = get_class('dashboard.deliveries.app', 'application')
    dosimeters_app = get_class('dashboard.dosimeters.app', 'application')
    default_products_app = get_class('dashboard.default_products.app', 'application')
    owners_app = get_class('dashboard.owners.app', 'application')
    instructions_app = get_class('dashboard.instructions.app', 'application')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^deliveries/', self.deliveries_app.urls),
            url(r'^dosimeters/', self.dosimeters_app.urls),
            url(r'^default-products/', self.default_products_app.urls),
            url(r'^owners/', self.owners_app.urls),
            url(r'^instructions/', self.instructions_app.urls),
        ]
        return self.post_process_urls(urls)


application = DashboardApplication()
