# -*- coding: utf-8 -*-
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from zinnia.models import Category
from zinnia.models import Entry


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Entry)
class EntryTranslationOptions(TranslationOptions):
    fields = ('title', 'lead', 'content')
