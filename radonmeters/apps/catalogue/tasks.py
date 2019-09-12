from celery.utils.log import get_task_logger
from oscar.core.loading import get_model

from taskapp.celery import app

logger = get_task_logger(__name__)


@app.task
def check_order_status(order_id):
    """
    Task for checking dosimeter status
    """
    Order = get_model('order', 'Order')
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    # TODO save statuses separately
    Dosimeter = get_model('catalogue', 'Dosimeter')
    statuses = []
    for l in order.lines.prefetch_related('dosimeters'):
        statuses.extend(l.dosimeters.values_list('status', flat=True))

    if all(s == Dosimeter.STATUS_CHOICES.on_store_side for s in statuses):
        order.status = 'delivery_to_client'
        order.save()
    elif all(s == Dosimeter.STATUS_CHOICES.completed for s in statuses):
        order.status = 'completed'
        order.save()
