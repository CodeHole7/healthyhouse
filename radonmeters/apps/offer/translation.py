# -*- coding: utf-8 -*-
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from oscar.core.loading import get_model

Range = get_model('offer', 'Range')
ConditionalOffer = get_model('offer', 'ConditionalOffer')


@register(Range)
class RangeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(ConditionalOffer)
class ConditionalOfferTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
