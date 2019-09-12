from django.conf.urls import url
from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class DefaultProductsDashboardConfig(DashboardApplication):
    """
    App for representation default products in the Oscar's Dashboard.
    """
    default_permissions = ['is_staff', ]

    product_list_view = get_class('dashboard.default_products.views', 'DefaultProductListView')
    product_detail_view = get_class('dashboard.default_products.views', 'DefaultProductUpdateView')

    def get_urls(self):
        urls = [
            url(r'^$',
                self.product_list_view.as_view(),
                name='default-product-list'),
            url(r'^(?P<pk>[-\w]+)/$',
                self.product_detail_view.as_view(),
                name='default-product-detail'),
        ]
        return self.post_process_urls(urls)


application = DefaultProductsDashboardConfig()
