import stripe as stripe_client
from django.conf import settings

# Default client overridden for adding `api_key`
# in one place (here).
stripe_client.api_key = settings.STRIPE_SK
stripe = stripe_client
