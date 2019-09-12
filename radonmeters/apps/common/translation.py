# -*- coding: utf-8 -*-
from django.contrib.flatpages.models import FlatPage
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from common.models import CategorySection
from common.models import DosimeterPDFReportTheme


@register(CategorySection)
class CategorySectionTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(FlatPage)
class FlatPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


@register(DosimeterPDFReportTheme)
class DosimeterPDFReportThemeTranslationOptions(TranslationOptions):
    fields = ('body',)
