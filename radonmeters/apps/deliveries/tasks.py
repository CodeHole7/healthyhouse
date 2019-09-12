import datetime

from django.db.models import Q

from customer.utils import get_email_templates, COMM_TYPE_SHIPMENT_REMIND
from common.tasks import send_mail_task
from deliveries.client import get_statuses_request
from deliveries.models import Shipment

from celery.utils.log import get_task_logger
from taskapp.celery import app
logger = get_task_logger(__name__)

@app.task
def update_shipment_statuses():
    """
    Update shipment statuses for all shipments which are not delivered yet.
    """
    shipments_data = Shipment.objects.filter(~(Q(current_status__exact='DELIVERED') | Q(current_status__exact='FAILED'))).values_list('data', flat=True) 
    shipment_ids = [item['id'] for item in shipments_data if item and item.get('id')]
    if not shipment_ids:
        return
    logger.info('Getting delivery statuses for %i shipments...' % len(shipment_ids))
    statuses_data = get_statuses_request(shipment_ids)
    statuses_data_actual = [s for s in statuses_data if s['current_status'] is not None]
    logger.info('Received delivery statuses for %i shipments' % len(statuses_data_actual))
    for item in statuses_data_actual:
        shipment = Shipment.objects.get(order__shipping_id__exact=item['shipment_id'])
        shipment.current_status = item['current_status']
        shipment.current_status_text = item['current_status_text']
        # Python prior to 3.7 does not recognize colon in timezone:
        if item['current_status_registered_at'][-3] == ':':
            item['current_status_registered_at'] = item['current_status_registered_at'][:-3]+item['current_status_registered_at'][-2:]
        shipment.current_status_registered_at = datetime.datetime.strptime(item['current_status_registered_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
        if (shipment.current_status != 'DELIVERED' and
            (datetime.datetime.now(tz=datetime.timezone.utc) - shipment.current_status_registered_at) > datetime.timedelta(days=21)):
            shipment.current_status = 'FAILED'
        shipment.save()


@app.task
def delivery_remind_pickup():
    """
    Send remind emails to customers about delivery
    """
    qs = Shipment.objects.filter(
        current_status='AVAILABLE_FOR_DELIVERY')

    for shipment in qs:
        # TODO optimized queryset
        if shipment.days_to_pick_up() in [1, 5, 10]:
            order = shipment.order

            context = {
                'order': order,
                'user': order.user
            }
            email_templates = get_email_templates(
                comm_type=COMM_TYPE_SHIPMENT_REMIND, context=context)
            send_mail_task.delay(
                email=order.user.email if order.user else order.guest_email,
                subject=email_templates.get('subject'),
                message=email_templates.get('message'),
                html_message=email_templates.get('html_message'),
                from_email=order.get_from_email(),
                connection=order.get_connection(),
            )
