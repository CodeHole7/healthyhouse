from django import forms
from oscar.apps.dashboard.promotions.forms import RawHTMLForm as BaseRawHTMLForm
from oscar.core.loading import get_model

RawHTML = get_model('promotions', 'RawHTML')


class RawHTMLForm(forms.ModelForm):
    """
    Overridden just for remove adding html class `no-widget-init`
    from `init` method.
    """

    class Meta(BaseRawHTMLForm.Meta):
        pass
