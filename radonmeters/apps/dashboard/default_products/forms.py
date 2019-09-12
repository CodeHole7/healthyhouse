from django import forms
from django.utils.translation import pgettext_lazy

from catalogue.models import DefaultProduct


class DefaultProductSearchForm(forms.Form):
    """
    Form for filtering default products in Oscar's Dashboard.
    """

    id = forms.UUIDField(
        required=False,
        label=pgettext_lazy("Default Product's ID", "ID"))
    serial_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Default Product's serial number", "Serial number"))
    order_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Default Product's order number", "Order number"))


class DefaultProductChangeForm(forms.ModelForm):
    """
    Form for edit default products in Oscar's Dashboard.
    """

    class Meta:
        model = DefaultProduct
        fields = ('line', 'serial_number',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['line'].disabled = True
