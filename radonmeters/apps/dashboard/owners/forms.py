from django import forms
from django.utils.translation import pgettext_lazy
from owners.models import OwnerEmailConfig


class OwnerDashboardSearchForm(forms.Form):
    """
    Form for filtering dosimeters in Oscar's Dashboard.
    """

    id = forms.IntegerField(
        required=False,
        label=pgettext_lazy("ID", "ID"))
    email = forms.EmailField(
        required=False,
        label=pgettext_lazy("Email", "Email"))


class OwnerDashboardEmailConfigForm(forms.ModelForm):

    class Meta:
        model = OwnerEmailConfig
        exclude = ['owner']

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

    def save(self, commit=True):
        self.instance.owner = self.owner
        return super().save(commit)
