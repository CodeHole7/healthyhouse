from django import forms
from django.utils.translation import pgettext_lazy

from oscar.core.loading import get_model

PartnerAddress = get_model('partner', 'PartnerAddress')


class PartnerAddressForm(forms.ModelForm):
    """Add field code"""
    name = forms.CharField(
        required=False, max_length=128,
        label=pgettext_lazy(u"Partner's name", u"Name"))
    code = forms.CharField(
        required=False, max_length=128,
        label=pgettext_lazy(u"Partner's code", u"Code"))

    class Meta:
        fields = ('name', 'line1', 'line2', 'line3', 'line4',
                  'state', 'postcode', 'country', 'code')
        model = PartnerAddress
