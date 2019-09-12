from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import ugettext as _
from oscar.apps.customer.forms import \
    PasswordChangeForm as CorePasswordChangeForm
from oscar.apps.customer.forms import ProfileForm as CoreProfileForm
from oscar.core.compat import existing_user_fields
from oscar.core.loading import get_class

EmailUserCreationForm = get_class('customer.forms', 'EmailUserCreationForm')


class ProfileForm(CoreProfileForm):
    """
    Overwritten for adding custom fields and placeholders.
    """

    class Meta:
        model = get_user_model()
        fields = existing_user_fields([
            'first_name', 'last_name', 'phone_number', 'email'])
        labels = {
            'first_name': _("Your First Name"),
            'last_name': _("Your Last Name"),
            'phone_number': _("Your Phone Number"),
            'email': _("Your E-mail")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set custom placeholders.
        self.fields['first_name'].widget.attrs['placeholder'] = _('Enter first name')
        self.fields['last_name'].widget.attrs['placeholder'] = _('Enter last name')
        self.fields['phone_number'].widget.attrs['placeholder'] = _('Enter phone number')
        self.fields['email'].widget.attrs['placeholder'] = _('Enter email')


class PasswordChangeForm(CorePasswordChangeForm):
    """
    Overwritten just for consistency of flow for overriding forms.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EmailUserCreationOnShippingAddressForm(EmailUserCreationForm):

    class Meta(EmailUserCreationForm.Meta):
        fields = list(EmailUserCreationForm.Meta.fields) + [
            'first_name', 'last_name', 'phone_number']


class ShippingAddressToUserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        check_fields = [getattr(self.instance, f) for f in self.fields]
        if any(check_fields):
            raise forms.ValidationError('You do not need to update fields.')
        return cleaned_data
