from django.conf.urls import url
from oscar.apps.customer.app import CustomerApplication as CoreCustomerApplication
from oscar.core.loading import get_class


class CustomerApplication(CoreCustomerApplication):
    """
    Overwritten for future's changes.
    """

    instruction_detail_view = get_class(
        'customer.views_custom',
        'InstructionDetailView')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^instructions/(?P<pk>[-\w]+)/$',
                self.instruction_detail_view.as_view(), name='instruction-detail'),
        ]
        return urls


application = CustomerApplication()
