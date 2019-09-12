from oscar.core.loading import get_model

from common.utils import render_to_email

CommunicationEventType = get_model('customer', 'CommunicationEventType')

COMM_TYPE_INSTRUCTION = 'INSTRUCTION_REPORT'
COMM_TYPE_DOSIMETER_REPORT = 'DOSIMETER_REPORT'
COMM_TYPE_CONTACT_US = 'CONTACT_US'
COMM_TYPE_SEND_VOUCHER = 'SEND_VOUCHER'
COMM_TYPE_SHIPMENT_REMIND = 'SHIPMENT_REMIND'
COMM_TYPE_LABEL = 'LABEL'
COMM_TYPE_RETURN_LABEL = 'RETURN_LABEL'
COMM_TYPE_INVOICE = 'INVOICE'
COMM_TYPE_DOSIMETERS_REGISTERED = 'DOSIMETERS_REGISTERED'

# Specified email templates collection, which need to override.
# For adding new item, need only set COMM_TYPE, and add templates.
# After that it will be available by specific comm code.
# Amount of templates unlimited.
# Need to keep on format (subject, message, html_message)
COMM_TYPES = {
    COMM_TYPE_DOSIMETER_REPORT: {
        'subject': 'common/email/dosimeters_report_subject_email.txt',
        'message': 'common/email/dosimeters_report_email_body.txt',
        'html_message': 'common/email/dosimeters_report_email_body.html'
    },
    COMM_TYPE_CONTACT_US: {
        'subject': 'common/email/mn_contact_us_subject_email.txt',
        'message': 'common/email/mn_contact_us_email.txt',
        'html_message': 'common/email/mn_contact_us_email.html',
    },
    COMM_TYPE_SEND_VOUCHER: {
        'subject': 'common/email/send_voucher_subject_email.txt',
        'message': 'common/email/send_voucher_body.txt',
        'html_message': 'common/email/send_voucher_body.html',
    },
    COMM_TYPE_INSTRUCTION: {
        'subject': 'common/email/instruction_report_subject_email.txt',
        'message': 'common/email/instruction_report_email_body.txt',
        'html_message': 'common/email/instruction_report_email_body.html',
    },
    COMM_TYPE_SHIPMENT_REMIND: {
        'subject': 'common/email/shipment_reminder_subject.txt',
        'message': 'common/email/shipment_reminder_body.txt',
        'html_message': 'common/email/shipment_reminder_body.html',
    },
    COMM_TYPE_LABEL: {
        'subject': 'common/email/label_subject.txt',
        'message': 'common/email/label_body.txt',
        'html_message': 'common/email/label_body.html',
    },
    COMM_TYPE_RETURN_LABEL: {
        'subject': 'common/email/return_label_subject.txt',
        'message': 'common/email/return_label_body.txt',
        'html_message': 'common/email/return_label_body.html',
    },
    COMM_TYPE_INVOICE: {
        'subject': 'common/email/invoice_subject.txt',
        'message': 'common/email/invoice_body.txt',
        'html_message': 'common/email/invoice_body.html',
    },
    COMM_TYPE_DOSIMETERS_REGISTERED: {
        'subject': 'common/email/dosimeters_registered_subject.txt',
        'message': 'common/email/dosimeters_registered_body.txt',
        'html_message': 'common/email/dosimeters_registered_body.html',
    },
}


def get_email_templates(
        comm_type: str,
        context: dict=None):
    """
    Get specific email templates, by communication event code.
    According to Oscar's flow, if email templates exists in DB
    we will take it, otherwise look for in templates folder.

    :param (str) comm_type: Communication event code.
    :param (dict) context: Dict with data for rendering in templates.
    :return (dict): Rendered to sting email templates.
    """

    if comm_type not in COMM_TYPES:
        raise NotImplementedError('Email templates can not be specified.')

    if context is None:
        context = {}

    # Try to get object from DB
    try:
        communication_event = CommunicationEventType.objects.get(code=comm_type)
        message = communication_event.get_messages(context)
        return {
            "subject": message.get('subject'),
            "message": message.get('body'),
            "html_message": message.get('html')}

    # If object doesn't exist in DB
    # We will take it from templates folder by default
    except CommunicationEventType.DoesNotExist:
        return {
            'subject': render_to_email(
                COMM_TYPES[comm_type]['subject'],
                context=context),
            'message': render_to_email(
                COMM_TYPES[comm_type]['message'],
                context=context),
            'html_message': render_to_email(
                COMM_TYPES[comm_type]['html_message'],
                context=context)}
