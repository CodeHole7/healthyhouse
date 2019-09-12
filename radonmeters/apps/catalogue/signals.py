from django.db.models.signals import post_save
from django.dispatch import receiver
from oscar.core.loading import get_model

from catalogue.tasks import check_order_status

Dosimeter = get_model('catalogue', 'Dosimeter')


@receiver(post_save, sender=Dosimeter, dispatch_uid="post_save_dosimeter")
def post_save_dosimeter(sender, instance, created, **kwargs):
    """
    Update order status if all dosimeters have the same status
    """
    if instance.status in [
            Dosimeter.STATUS_CHOICES.on_store_side, Dosimeter.STATUS_CHOICES.completed]:
        check_order_status.delay(instance.line.order_id)
