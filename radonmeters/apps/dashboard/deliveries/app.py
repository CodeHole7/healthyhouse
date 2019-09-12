from django.conf.urls import url
from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class DeliveriesDashboardConfig(DashboardApplication):
    """
    App for representation instances of deliveries app
    in the Oscar's Dashboard.
    """
    default_permissions = ['is_staff', ]

    shipment_list_view = get_class(
        'dashboard.deliveries.views',
        'ShipmentListView')
    shipment_create_view = get_class(
        'dashboard.deliveries.views',
        'ShipmentCreateView')
    shipment_update_view = get_class(
        'dashboard.deliveries.views',
        'ShipmentUpdateView')
    shipment_delete_view = get_class(
        'dashboard.deliveries.views',
        'ShipmentDeleteView')
    shipment_return_create_view = get_class(
        'dashboard.deliveries.views',
        'ShipmentReturnCreateView')
    shipment_return_update_view = get_class(
        'dashboard.deliveries.views',
        'ShipmentReturnUpdateView')

    def get_urls(self):
        urls = [
            url(r'^$',
                self.shipment_list_view.as_view(),
                name='shipment-list'),
            url(r'^add/',
                self.shipment_create_view.as_view(),
                name='shipment-create'),
            url(r'^return/add/$',
                self.shipment_return_create_view.as_view(),
                name='shipment-return-create'),
            url(r'^return/(?P<pk>[-\w]+)/$',
                self.shipment_return_update_view.as_view(),
                name='shipment-return-update'),
            url(r'^(?P<pk>[-\w]+)/$',
                self.shipment_update_view.as_view(),
                name='shipment-update'),
            url(r'^(?P<pk>[-\w]+)/delete/$',
                self.shipment_delete_view.as_view(),
                name='shipment-delete')]
        return self.post_process_urls(urls)


application = DeliveriesDashboardConfig()
