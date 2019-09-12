from django import forms
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices


class SortForm(forms.Form):

    CHOICES = Choices(
        ('-date_updated', '-date_updated', _('Newest')),
        ('-stockrecords__price_excl_tax', '-stockrecords__price_excl_tax', _('Price high to low')),
        ('stockrecords__price_excl_tax', 'stockrecords__price_excl_tax', _('Price low to high')),
        ('title', 'title', _('Title A to Z')),
        ('-title', '-title', _('Title Z to A')))

    sort_by = forms.ChoiceField(choices=CHOICES._doubles, required=False)
