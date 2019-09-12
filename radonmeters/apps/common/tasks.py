from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import mail_admins
from django.core.mail import mail_managers
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend

from config import settings
from taskapp.celery import app

logger = get_task_logger(__name__)


@app.task
def mail_admins_task(
        subject: str,
        message: str,
        fail_silently: bool=False,
        connection: EmailBackend=None,
        html_message: str=None):
    """
    Task for async call default `mail_admins`.
    """

    mail_admins(subject, message, fail_silently, connection, html_message)

    logger.info('Mails sent to admins.')


@app.task
def mail_managers_task(
        subject: str,
        message: str,
        fail_silently: bool=False,
        connection: EmailBackend=None,
        html_message: str=None):
    """
    Task for async call default `mail_managers`.
    """

    mail_managers(subject, message, fail_silently, connection, html_message)

    logger.info('Mails sent to managers.')


@app.task
def send_mail_task(subject, message, email, from_email=None, **kwargs):
    """
    Sends email notification, based on gotten parameters.
    """

    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

    subject = subject.replace('\n', '')
    send_mail(subject, message, from_email, [email], **kwargs)

    logger.info('Mail sent to `%s`.' % email)


@app.task
def send_mails_task(subject, message, emails, from_email=None, **kwargs):
    """
    Sends email notifications, based on gotten parameters.

    One subject and message to many recipients
    """

    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, message, from_email, emails, **kwargs)

    logger.info('Mails sent to %s.' % ', '.join(emails))
