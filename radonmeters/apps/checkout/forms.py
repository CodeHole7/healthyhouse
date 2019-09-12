import uuid
from copy import copy

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from model_utils.choices import Choices
from oscar.apps.address.forms import AbstractAddressForm
from oscar.core.loading import get_model

from common.utils import render_to_email
from common.validators import PhoneNumberValidator
from customer.forms import EmailUserCreationOnShippingAddressForm, ShippingAddressToUserForm

Country = get_model('address', 'Country')


class ShippingAddressForm(AbstractAddressForm):
    """
    Overridden for adding/excluding logic.

    Excluded `PhoneNumberMixin` from list of bases classes (MRO).

    Added fields:
    - email;

    Removed fields:
    - title;

    Synced first_name, last_name, phone to user data if it is empty.
    """

    email = forms.EmailField()
    phone_number = forms.CharField(validators=[PhoneNumberValidator()])

    class Meta:
        model = get_model('order', 'shippingaddress')
        fields = [
            'email', 'first_name', 'last_name',
            'line1', 'line2', 'line3', 'line4',
            'state', 'postcode', 'country',
            'phone_number', 'notes']
        labels = {
            'state': 'State',
            'notes': 'Comments to order'}

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request
        self.adjust_country_field()

        # Adding placeholders
        self.fields['email'].widget.attrs.update({'placeholder': _('Enter email')})
        self.fields['first_name'].widget.attrs.update({'placeholder': _('Enter first name')})
        self.fields['last_name'].widget.attrs.update({'placeholder': _('Enter last name')})
        self.fields['line1'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['line2'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['line3'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['line4'].widget.attrs.update({'placeholder': _('Enter address')})
        self.fields['state'].widget.attrs.update({'placeholder': _('Enter state')})
        self.fields['postcode'].widget.attrs.update({'placeholder': _('Enter code')})
        self.fields['phone_number'].widget.attrs.update({'placeholder': _('Enter number')})
        self.fields['notes'].widget.attrs.update({'placeholder': _('Enter comments here')})

        # Adding placeholder for `country` if it is available.
        country = self.fields.get('country')
        if country is not None:
            country.widget.attrs.update({'placeholder': _('Choose country')})

        # Add custom logic if user is authenticated.
        if self.request.user.is_authenticated:

            # Add initial value for some fields, which we have in user model.
            self.fields['first_name'].initial = self.request.user.first_name
            self.fields['last_name'].initial = self.request.user.last_name
            self.fields['phone_number'].initial = self.request.user.phone_number
            self.fields['email'].initial = self.request.user.email

            # Disable email field, user can't use not his email here.
            self.fields['email'].disabled = True

    def adjust_country_field(self):
        countries = Country._default_manager.filter(is_shipping_country=True)

        # No need to show country dropdown if there is only one option
        if len(countries) == 1:
            self.fields.pop('country', None)
            self.instance.country = countries[0]
        else:
            self.fields['country'].queryset = countries
            self.fields['country'].empty_label = None

    def clean(self):
        super().clean()

        phone_number = self.cleaned_data.get('phone_number', '')
        user_data = {
            'email': self.cleaned_data.get('email', ''),
            'first_name': self.cleaned_data.get('first_name', ''),
            'last_name': self.cleaned_data.get('last_name', ''),
            'phone_number': phone_number,
        }

        try:
            PhoneNumberValidator()(phone_number)
        except ValidationError:
            self.errors.update({'phone_number': [PhoneNumberValidator.message]})
        else:
            # Apply the next actions only when current user is not authenticated.
            if not self.request.user.is_authenticated:

                # Generate password.
                _password = uuid.uuid4().hex

                # Prepare data for validating an email.
                data = copy(user_data)
                data.update({
                    'password1': _password,
                    'password2': _password,
                })

                # Validate data (with email) by form.
                sub_form = EmailUserCreationOnShippingAddressForm(data=data)

                if sub_form.is_valid():
                    # Create user object.
                    user = sub_form.save()

                    # Prepare context for email.
                    _context = {'password': _password}

                    # Prepare data for email.
                    subject = render_to_string(
                        'customer/emails/commtype_registration_subject.txt')
                    message = render_to_email(
                        'customer/emails/commtype_registration_body.txt',
                        context=_context)
                    html_message = render_to_email(
                        'customer/emails/commtype_registration_body.html',
                        context=_context)

                    # Send email to user.
                    user.email_user(
                        subject=subject,
                        message=message,
                        html_message=html_message)
                else:
                    # Update `errors` with errors from sub_form.
                    self.errors.update(**sub_form.errors)
            else:
                # tried to set shipping_address to user if it was empty
                user_data.pop('email')
                sub_form = ShippingAddressToUserForm(
                    instance=self.request.user, data=user_data)
                if sub_form.is_valid():
                    sub_form.save()


class CheckoutGatewayForm(forms.Form):
    """
    Form for providing to user the several ways of making a checkout.
    """

    TYPE_CHOICES = Choices(
        ('guest', 'guest', _('I am a new customer.')),
        ('customer', 'customer', _('I am a returning customer.')))

    user_type = forms.ChoiceField(
        label=_('Who are you?'),
        widget=forms.RadioSelect,
        choices=TYPE_CHOICES._doubles)
