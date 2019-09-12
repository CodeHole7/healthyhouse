from django import forms
from django.utils.translation import ugettext_lazy as _

from common.models import ConsultationRequest
from common.models import ContactUsRequest
from common.models import SubscribeRequest
from common.models import DosimeterPDFReportTheme


class SubscribeRequestForm(forms.ModelForm):
    """
    Form for creating requests on subscribe.
    """

    class Meta:
        model = SubscribeRequest
        fields = ('email',)


class ConsultationRequestForm(forms.ModelForm):
    """
    Form for creating requests on consultation.
    """

    class Meta:
        model = ConsultationRequest
        fields = ('name', 'phone_number', 'email')


class ContactUsRequestForm(forms.ModelForm):
    """
    Form for creating messages.

    The copy of this instance will be sent to all managers of site,
    if the settings does not cancel this behavior.
    """

    class Meta:
        model = ContactUsRequest
        fields = ('name', 'email', 'message')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.user.is_authenticated:
            self.instance.user = self.user
        return super().save(commit)


class DosimeterPDFReportThemeAdminForm(forms.ModelForm):
    """
    Form for DosimeterPDFReportTheme in admin panel
    """

    class Meta:
        model = DosimeterPDFReportTheme
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].required = True

    def clean(self):
        cleaned_data = super().clean()
        min_value = cleaned_data.get('min_concentration')
        max_value = cleaned_data.get('max_concentration')
        if min_value is not None and max_value is not None and \
                min_value > max_value:
            raise forms.ValidationError({
                'min_concentration':
                    _('Min_concentration should be more than max_concentration.')})
        return cleaned_data
