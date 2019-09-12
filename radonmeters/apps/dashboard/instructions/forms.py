# -*- coding: utf-8 -*-
from django import forms
from django.template import Template, TemplateSyntaxError
from django.template.loader import get_template
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_model

Instruction = get_model('instructions', 'Instruction')
InstructionTemplate = get_model('instructions', 'InstructionTemplate')
Order = get_model('order', 'Order')


class InstructionTemplateForm(forms.ModelForm):
    preview_order_number = forms.CharField(
        label=_("Order number"), required=False)
    is_active = forms.BooleanField(
        label=_('Is active?'), required=False, initial=True)

    class Meta:
        model = InstructionTemplate
        fields = [
            'pdf_template', 'preview_order_number', 'is_active']

    def __init__(self, data=None, initial=None, *args, **kwargs):
        self.render_preview = False
        if data:
            self.render_preview = 'render_preview' in data
        if not kwargs.get('instance'):
            initial = initial or {}
            t = get_template('dashboard/instructions/template_default.html')
            initial['pdf_template'] = t.template.source
        super(InstructionTemplateForm, self).__init__(data, initial=initial, *args, **kwargs)
        self.fields['pdf_template'].widget.attrs.update(
            {
                'class': 'no-widget-init',
                'style': 'resize: none; width: 100%; min-height: 600px; height: 600px;'
             })

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active', True)
        if not InstructionTemplate.can_change_is_active(self.instance, is_active):
            raise forms.ValidationError(_('At least one template should be active'))
        return is_active

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
        except Order.DoesNotExist:
            raise forms.ValidationError(_(
                "No order found with this number"))
        return number


class InstructionListCreateForm(forms.ModelForm):

    class Meta:
        fields = ('orders', )

    def save(self, commit=True):
        return super().save(commit)
