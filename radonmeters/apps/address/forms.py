from django.utils.translation import ugettext as _
from oscar.apps.address.forms import AbstractAddressForm
from oscar.core.loading import get_model

UserAddress = get_model('address', 'UserAddress')


class UserAddressForm(AbstractAddressForm):
    """
    Overridden only for excluding `PhoneNumberMixin` from bases classes (MRO).

    The all code in this class is default realisation,
    we just copied it from default `UserAddressForm` and pasted here.
    """

    class Meta:
        model = UserAddress
        fields = [
            'title', 'first_name', 'last_name',
            'line1', 'line2', 'line3', 'line4',
            'state', 'postcode', 'country',
            'phone_number', 'notes',
        ]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = user

        # Adding placeholders
        self.fields['title'].widget.attrs.update({'placeholder': _('Enter title')})
        self.fields['first_name'].widget.attrs.update({'placeholder': _('Enter first name')})
        self.fields['last_name'].widget.attrs.update({'placeholder': _('Enter last name')})
        self.fields['line1'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['line2'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['line3'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['line4'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['state'].widget.attrs.update({'placeholder': _('Enter state')})
        self.fields['postcode'].widget.attrs.update({'placeholder': _('Enter code')})
        self.fields['country'].widget.attrs.update({'placeholder': _('Enter country')})
        self.fields['phone_number'].widget.attrs.update({'placeholder': _('Enter number')})
        self.fields['notes'].widget.attrs.update({'placeholder': _('Enter comments here')})
