# -*- coding: utf-8 -*-
from django import forms
from django.template import Template, TemplateSyntaxError
from django.template.loader import get_template
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_model

from owners.models import Owner
from owners.models import OwnerPDFReportTheme

Order = get_model('order', 'Order')


class OwnerDetailForm(forms.ModelForm):

    class Meta:
        model = Owner
        fields = '__all__'

    def clean_is_default(self):
        is_default = self.cleaned_data.get('is_default', False)
        return Owner.validate_is_default(self.instance, is_default)


class OwnerPDFReportThemeForm(forms.ModelForm):
    preview_order_number = forms.CharField(
        label=_("Order number"), required=False)

    class Meta:
        model = OwnerPDFReportTheme
        fields = [
            'pdf_template', 'preview_order_number', 'logo', 'owner']

    def __init__(self, data=None, initial=None, *args, **kwargs):
        self.render_preview = False
        if data:
            self.render_preview = 'render_preview' in data
        if not kwargs.get('instance'):
            initial = initial or {}
            t = get_template('pdf/dosimeters_report.html')
            initial['pdf_template'] = t.template.source
        super(OwnerPDFReportThemeForm, self).__init__(data, initial=initial, *args, **kwargs)
        self.fields['pdf_template'].widget.attrs.update(
            {
                'class': 'no-widget-init',
                'style': 'resize: none; width: 100%; min-height: 600px; height: 600px;'
             })

    def clean_pdf_template(self):
        body = self.cleaned_data['pdf_template']
        try:
            Template(body)
        except TemplateSyntaxError as e:
            raise forms.ValidationError(six.text_type(e))
        return body

    def clean_preview_order_number(self):
        number = self.cleaned_data['preview_order_number'].strip()
        if not self.render_preview:
            return number
        try:
            self.preview_order = Order.objects.get(number=number)
            if not self.preview_order.dosimeters_pdf_report_can_be_generated:
                raise forms.ValidationError(_(
                    "We cannot generate report for this order."))
        except Order.DoesNotExist:
            raise forms.ValidationError(_(
                "No order found with this number"))
        return number
