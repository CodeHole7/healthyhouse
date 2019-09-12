import uuid

from django import template
from django.urls import reverse

from common.templatetags.base_context import site_url

from url_shortener.models import make_short_url_id

register = template.Library()


@register.simple_tag(takes_context=True)
def build_instruction_link(context):
    obj_id = context.get('instruction_id', uuid.uuid4())
    return site_url() + reverse('customer:instruction-detail', args=(obj_id,))

@register.simple_tag(takes_context=True)
def build_short_instruction_link(context):
    original_link = build_instruction_link(context)
    return site_url() + reverse('url_shortener:short_url', kwargs={'short_id': make_short_url_id(original_link)})