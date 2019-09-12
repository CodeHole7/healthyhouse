# -*- coding: utf-8 -*-
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from oscar.core.loading import get_model

RawHTML = get_model('promotions', 'RawHTML')


@register(RawHTML)
class RawHTMLTranslationOptions(TranslationOptions):
    fields = ('body',)
