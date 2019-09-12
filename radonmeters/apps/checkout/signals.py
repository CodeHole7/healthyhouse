from django.dispatch import receiver
from django.utils import timezone
from oscar.apps.checkout.signals import post_checkout


@receiver(post_checkout, dispatch_uid='order_post_checkout')
def order_post_checkout(sender, order, **kwargs):
    """
    Update is_paid for order after payment
    """

    order.is_paid = True
    order.payment_date = timezone.now()
    order.save()
