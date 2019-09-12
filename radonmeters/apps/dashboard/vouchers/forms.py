from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class
from oscar.core.loading import get_model
from oscar.forms import widgets

from common.tasks import send_mail_task
from customer.utils import COMM_TYPE_SEND_VOUCHER
from customer.utils import get_email_templates

Voucher = get_model('voucher', 'Voucher')
Benefit = get_model('offer', 'Benefit')
Range = get_model('offer', 'Range')
Condition = get_model('offer', 'Condition')
ConditionalOffer = get_model('offer', 'ConditionalOffer')
BaseVoucherForm = get_class('dashboard.vouchers.forms', 'VoucherForm')


class VoucherForm(BaseVoucherForm):
    """
    Overridden for removing validation on unique name,
    because instance of Voucher can be with non-unique name and it's ok.
    """

    def clean_name(self):
        return self.cleaned_data['name']


class VoucherBulkCreateForm(forms.Form):
    """
    Form for creating one or many instances of Voucher model.
    """

    BENEFIT_TYPES = (
        (Benefit.PERCENTAGE, _('Percentage off of products in range')),
        (Benefit.FIXED, _('Fixed amount off of products in range')))

    name = forms.CharField(label=_("Name"))
    quantity = forms.IntegerField(
        initial=1, label=_('Quantity'),
        help_text=_('How many vouchers will be generated.'))

    start_datetime = forms.DateTimeField(
        label=_('Start datetime'),
        widget=widgets.DateTimePickerInput())
    end_datetime = forms.DateTimeField(
        label=_('End datetime'),
        widget=widgets.DateTimePickerInput())

    usage = forms.ChoiceField(choices=Voucher.USAGE_CHOICES, label=_("Usage"))

    benefit_range = forms.ModelChoiceField(
        label=_('Which products get a discount?'),
        queryset=Range.objects.all())
    benefit_type = forms.ChoiceField(choices=BENEFIT_TYPES, label=_('Discount type'))
    benefit_value = forms.DecimalField(label=_('Discount value'))

    def clean(self):
        cleaned_data = super().clean()

        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        if start_datetime and end_datetime and end_datetime < start_datetime:
            raise forms.ValidationError(
                _("The start date must be before the end date."))

        return cleaned_data


class VoucherSendEmailForm(forms.Form):
    """
    Form for sending email to user with voucher (discount code).
    """

    voucher = forms.ModelChoiceField(
        queryset=Voucher.objects.filter(
            start_datetime__lte=timezone.now(),
            end_datetime__gte=timezone.now()).order_by('start_datetime'))
    user = forms.ModelChoiceField(
        required=False,
        queryset=get_user_model().objects.filter(is_active=True))
    email = forms.EmailField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        # Prepare vars.
        user = cleaned_data.get('user')
        email = cleaned_data.get('email')
        voucher = cleaned_data.get('voucher')

        # Check that only `user` or `email` was added.
        if all([user, email]) or not any([user, email]):
            self.add_error(None, _('Please choose User or add Email.'))

        # Check voucher can be used by chosen user.
        if user and voucher:
            is_available, message = voucher.is_available_to_user(user)
            if not is_available:
                self.add_error('voucher', message)

        # Send email to customer.
        # Try to find template in db or stored on drive...
        try:
            email_templates = get_email_templates(
                comm_type=COMM_TYPE_SEND_VOUCHER,
                context={'code': voucher.code})
            send_mail_task.delay(
                email=user.email if user else email,
                subject=email_templates['subject'],
                message=email_templates['message'],
                html_message=email_templates['html_message'])
        # ...when it not found, send simple message.
        except NotImplementedError:
            send_mail_task.delay(
                email=user.email if user else email,
                subject=_('You get a discount coupon.'),
                message=_('Coupon code: %s.') % voucher.code)

        # Return to default behavior.
        return cleaned_data
