from django.apps import AppConfig


class StripeConfig(AppConfig):
    name = 'providers.stripe_app'
    verbose_name = 'Payment Systems: Stripe'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import providers.stripe_app.signals
