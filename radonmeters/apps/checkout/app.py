from oscar.apps.checkout.app import CheckoutApplication as CoreCheckoutApplication

from oscar.core.loading import get_class
from checkout.views import stripe_client_secret, stripe_error_return
from django.conf.urls import url


class CheckoutApplication(CoreCheckoutApplication):
    """
    Overwritten for using in the future.
    """

    def get_urls(self):
        urls = super().get_urls()
        urls = urls + [
            url(r'^stripe-client-secret/(\w+)$',
            stripe_client_secret,
            name='stripe_client_secret'),
            url(r'^stripe-error-return/(\w+)$',
            	stripe_error_return, 
            	name="stripe_error_return")
        ]
        return self.post_process_urls(urls)

application = CheckoutApplication()
