from constance import config
from django import template
from django.conf import settings
from django.contrib.sites.models import Site

from common.utils import get_protocol

register = template.Library()


@register.simple_tag
def base_config():
    return config


@register.simple_tag
def site_url():
    return '{protocol}://{domain}'.format(
        protocol=get_protocol(),
        domain=Site.objects.get_current().domain)


@register.simple_tag
def media_url():
    return settings.MEDIA_URL
