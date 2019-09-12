from django import forms
from django.contrib import admin
from django.template import Template, TemplateSyntaxError
from django.template.loader import get_template
from django.utils import six

from owners.models import Owner
from owners.models import OwnerEmailConfig
from owners.models import OwnerPDFReportTheme


class OwnerEmailConfigAdminInline(admin.StackedInline):
    model = OwnerEmailConfig


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    model = Owner
    list_display = ('get_full_name', 'is_default')
    inlines = [OwnerEmailConfigAdminInline]


class OwnerPDFReportThemeAdminForm(forms.ModelForm):

    class Meta:
        model = OwnerPDFReportTheme
        fields = '__all__'

    def get_initial_for_field(self, field, field_name):
        initial = super().get_initial_for_field(field, field_name)
        if field_name == 'pdf_template' and not initial:
            t = get_template('pdf/dosimeters_report.html')
            return t.template.source
        return initial

    def clean_pdf_template(self):
        pdf_template = self.cleaned_data['pdf_template']
        try:
            Template(pdf_template)
        except TemplateSyntaxError as e:
            raise forms.ValidationError(six.text_type(e))
        return pdf_template


@admin.register(OwnerPDFReportTheme)
class OwnerPDFReportThemeAdmin(admin.ModelAdmin):
    form = OwnerPDFReportThemeAdminForm
