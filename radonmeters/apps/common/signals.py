from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from common.models import ContactUsRequest
from common.tasks import mail_managers_task
from common.utils import render_to_email
from customer.utils import COMM_TYPE_CONTACT_US
from customer.utils import get_email_templates

logger = get_task_logger(__name__)


@receiver(post_save, sender=ContactUsRequest)
def post_save_contact_us_request(sender, instance, created, **kwargs):
    """
    Does next actions:
    - Sends email to managers.
    """
    if created and settings.CONTACT_US_NOTIFICATION:
        context = {
            'name': instance.name,
            'email': instance.email,
            'message': instance.message,
            'admin_url': instance.get_admin_url()}
        try:
            email_templates = get_email_templates(COMM_TYPE_CONTACT_US, context)
            if email_templates:
                mail_managers_task.delay(
                    subject=email_templates.get('subject'),
                    message=email_templates.get('message'),
                    html_message=email_templates.get('html_message'))
        except NotImplementedError as exc:
            logger.error('Can not find email templates. Exception: %s' % exc)
