# -*- coding: utf-8 -*-
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from oscar.core.loading import get_model

CommunicationEventType = get_model('customer', 'CommunicationEventType')


@register(CommunicationEventType)
class CommunicationEventTypeTranslationOptions(TranslationOptions):
    fields = ('email_subject_template', 'email_body_template', 'email_body_html_template')
