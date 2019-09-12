import pathlib

from babel.numbers import format_currency
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from django.http import HttpRequest
from django.template.base import Template, VariableDoesNotExist
from django.template.loader import render_to_string
from weasyprint import HTML


def render_to_email(
        template_name: str,
        context: dict=None,
        request: HttpRequest=None,
        using: bool=None) -> str:
    """
    Calls default `render_to_string` from `django.template.loader`,
    with patching context.
    """

    if context is None:
        context = {}

    context.update({
        'SITE_URL': '%s://%s' % (
            get_protocol(),
            Site.objects.get_current().domain)})

    return render_to_string(template_name, context, request, using)


def get_protocol() -> str:
    """
    Returns sting with protocol of site.
    """

    if getattr(settings, 'SECURE_SSL_REDIRECT', False):
        return 'https'
    else:
        return 'http'


def get_client_ip(request) -> str:
    """
    Returns clients IP by data from request.
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def custom_format_currency(number, currency=None) -> str:
    """
    Provides more simple call for default `babel.numbers.format_currency`.
    """

    # Set default currency as currency if currency is not passed.
    if currency is None:
        currency = settings.OSCAR_DEFAULT_CURRENCY

    # Try to get currency format from settings.
    try:
        frm = settings.OSCAR_CURRENCY_FORMAT[currency]['format']
    except KeyError:
        frm = settings.OSCAR_CURRENCY_FORMAT[None]['format']

    # Format and return string with currency.
    return format_currency(number=number, currency=currency, format=frm)


def create_invoice_pdf(order, context, in_memory=False):
    """
    Generates invoice as pdf file.

    :return: Path to file.
    """
    file_name = 'invoice_%s.pdf' % order.number
    html = render_to_string('invoice.html', context=context)

    # Generate path to directory and create dir if it is doesn't exist yet.
    dir_path = '{}/{}'.format(settings.MEDIA_ROOT, 'invoices')
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

    path = '{dir_path}/{file_name}'.format(
        dir_path=dir_path,
        file_name=file_name)

    if in_memory:
        return HTML(string=html, base_url=settings.STATIC_ROOT).write_pdf()
    else:
        HTML(string=html, base_url=settings.STATIC_ROOT).write_pdf(path)
        return path


# Cryptography
# =============================================================================
cipher_suite = Fernet(settings.FERNET_KEY)


def encrypt(value):
    return cipher_suite.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt(value):
    return cipher_suite.decrypt(value.encode('utf-8')).decode('utf-8')


def create_file(path):
    """
    Create file object from string-path
    :param path:
    :return: File object
    """
    if path:
        open_file = open(path, "rb")
        file = File(open_file)

        return file


def get_allowed_language_code(language_code: str):
    """
    Tries to find language_code in allowed language codes.

    :param language_code: For example 'en' or 'nb'.
    :return: language_code or None.
    """

    norwegian_codes = {'no', 'nn', 'nb'}
    codes = {l[0].lower() for l in settings.LANGUAGES} | norwegian_codes
    target_code = language_code.lower()

    if target_code in codes:
        # We need to return 'nn' for all norwegian's codes.
        if target_code in norwegian_codes:
            return 'nn'
        else:
            return target_code


def is_radosure():
    return settings.MAIN_PERMISSION == settings.RADOSURE_NAME


def render_html_preview(template: Template, context: dict, as_image=True):
    try:
        html = template.render(context)
    except VariableDoesNotExist:
        return _('Error during report rendering.')

    # Generate and return report file.
    html = HTML(
        string=html,
        encoding='UTF-8',
        base_url=settings.MEDIA_ROOT
    )
    if as_image:
        return html.write_png()
    return html.write_pdf()
