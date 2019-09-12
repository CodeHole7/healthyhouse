# -*- coding: utf-8 -*-
import logging
from subprocess import call

from ckeditor.fields import RichTextFormField
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.flatpages.models import FlatPage
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import TemplateView
from modeltranslation.admin import TranslationAdmin
from oscar.core.loading import get_model

from common.forms import DosimeterPDFReportThemeAdminForm
from common.models import CategorySection, DosimeterPDFReportTheme
from common.models import ConsultationRequest
from common.models import ContactUsRequest
from common.models import SubscribeRequest

logger = logging.getLogger(__name__)
RawHTML = get_model('promotions', 'RawHTML')


class FlatPageAdmin(TranslationAdmin):
    """
    Overridden for using TranslationAdmin and RichTextFormField.
    """
    model = FlatPage

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if isinstance(getattr(field, 'widget', None), AdminTextareaWidget):
            field = RichTextFormField(required=field.required)
        self.patch_translation_field(db_field, field, **kwargs)
        return field


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)


@admin.register(ContactUsRequest)
class ContactUsRequestAdmin(admin.ModelAdmin):
    model = ContactUsRequest
    search_fields = ('name', 'email', 'user__email', 'user__id')
    list_filter = ('created',)
    list_display = ('created', 'name', 'email', 'user')
    readonly_fields = ('created', 'modified', 'user', 'name', 'email')
    fields = ('name', 'email', 'user', 'message')


@admin.register(SubscribeRequest)
class SubscribeRequest(admin.ModelAdmin):
    model = SubscribeRequest
    search_fields = ('email',)
    list_filter = ('created',)
    list_display = ('email', 'created')
    fields = ('email',)


@admin.register(ConsultationRequest)
class ConsultationRequest(admin.ModelAdmin):
    model = ConsultationRequest
    search_fields = ('email', 'name', 'phone_number')
    list_filter = ('created', 'is_answered')
    list_display = ('email', 'name', 'phone_number', 'created', 'is_answered')
    fields = ('name', 'phone_number', 'email', 'is_answered')


@admin.register(CategorySection)
class CategorySectionAdmin(TranslationAdmin):
    model = CategorySection
    list_filter = ('category',)
    list_display = ('title', 'category', 'position',)
    list_editable = ('position',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if isinstance(getattr(field, 'widget', None), AdminTextareaWidget):
            field = RichTextFormField(required=field.required)
        self.patch_translation_field(db_field, field, **kwargs)
        return field


@admin.register(DosimeterPDFReportTheme)
class DosimeterPDFReportThemeAdmin(TranslationAdmin):
    model = DosimeterPDFReportTheme
    list_display = ('owner', 'min_concentration', 'max_concentration')
    list_filter = ('owner', )
    list_select_related = ('owner', )
    form = DosimeterPDFReportThemeAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if isinstance(getattr(field, 'widget', None), AdminTextareaWidget):
            field = RichTextFormField(required=field.required)
        self.patch_translation_field(db_field, field, **kwargs)
        return field


class RestartSupervisorView(TemplateView):
    template_name = 'admin/restart_confirm.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            if settings.DEBUG:
                call(['echo', 'Supervisorctl was restarted'])
            else:
                call(['supervisorctl', 'restart', 'all'])
            logger.info('Server has been restarted')
            return HttpResponse('Server has been restarted')
        return HttpResponseForbidden()
