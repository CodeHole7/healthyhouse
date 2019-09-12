# -*- coding: utf-8 -*-
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from oscar.core.loading import get_model

CommunicationEventType = get_model('customer', 'CommunicationEventType')


@admin.register(CommunicationEventType)
class CommunicationEventTypeAdmin(TranslationAdmin):
    model = CommunicationEventType
