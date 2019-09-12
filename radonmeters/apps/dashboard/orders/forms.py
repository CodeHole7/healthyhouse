from django.core.exceptions import ValidationError
from django import forms
from django.urls import reverse
from django.utils.translation import pgettext_lazy

from common.validators import PhoneNumberValidator

from oscar.apps.dashboard.orders.forms import OrderSearchForm as OrderSearchFormBase

APPROVAL_STATUS_CHOICES = (
    ('does_not_matter', pgettext_lazy('Does not matter', 'Does not matter')),
    ('ready_for_approval_and_not_approved', pgettext_lazy('Ready for approval but not approved', 'Ready for approval but not approved')),
    ('approved', pgettext_lazy('Approved', 'Approved')),
    ('not_ready_for_approval_and_not_approved', pgettext_lazy('Not ready for approval and not approved', 'Not ready for approval and not approved')),
)

REPORT_STATUS_CHOICES = (
    ('does_not_matter', pgettext_lazy('Does not matter', 'Does not matter')),
    ('sent', pgettext_lazy('Report is sent', 'Report is sent')),
    ('reported', pgettext_lazy('Reported by partner', 'Reported by partner')),
    ('not reported', pgettext_lazy('Not reported by partner', 'Not reported by partner')),
    ('sent_or_reported', pgettext_lazy('Report is sent or reported by partner', 'Report is sent or reported by partner')),
    ('not_sent_and_not_reported', pgettext_lazy('Report is not sent and not reported by partner', 'Report is not sent and not reported by partner')),
    ('sent_and_reported', pgettext_lazy('Report is sent and reported by partner', 'Report is sent and reported by partner')),
)

ANALYSIS_STATUS_CHOICES = (
    ('does_not_matter', pgettext_lazy('Does not matter', 'Does not matter')),
    ('no_slip_result', pgettext_lazy('Result OK, no slip inserted', 'Result OK, no slip inserted')),
    ('no_result_slip', pgettext_lazy('Slip OK, no lab inserted', 'Slip OK, no lab inserted')),
    ('empty', pgettext_lazy('No data is present', 'No data is present')),
    ('partial', pgettext_lazy('Some data is missing', 'Some data is missing')),
)

WEIRDNESS_STATUS_CHOICES = (
    ('does_not_matter', pgettext_lazy('Does not matter', 'Does not matter')),
    ('outlier', pgettext_lazy('Outlier concentration', 'Outlier concentration')),
    ('level_1_overlap', pgettext_lazy('Level 1 floor metric', 'Level 1 floor metric')),
    ('level_2_overlap', pgettext_lazy('Level 2 floor metric', 'Level 2 floor metric')),
)

ORDER_STATUS_CHOICES = (
    ('does_not_matter', pgettext_lazy('Does not matter', 'Does not matter')),
    ('not canceled', pgettext_lazy('not canceled', 'not canceled')),
    ('created', pgettext_lazy('created', 'created')),
    ('issued', pgettext_lazy('issued', 'issued')),
    ('delivery_to_client', pgettext_lazy('delivery_to_client', 'delivery_to_client')),
    ('completed', pgettext_lazy('completed', 'completed')),
    ('canceled', pgettext_lazy('canceled', 'canceled')),
)

SHIPMENT_STATUS_CHOICES = (
    ('does_not_matter', pgettext_lazy('Does not matter', 'Does not matter')),
    ('UNKNOWN', pgettext_lazy('Unknown', 'Unknown')),
    ('INFORMED', pgettext_lazy('Informed', 'Informed')),
    ('GENERAL', pgettext_lazy('General', 'General')),
    ('EN_ROUTE', pgettext_lazy('En route', 'En route')),
    ('AVAILABLE_FOR_DELIVERY', pgettext_lazy('Available for delivery', 'Available for delivery')),
    ('DELIVERED', pgettext_lazy('Delivered', 'Delivered')),
    ('FAILED', pgettext_lazy('Failed', 'Failed')),
#    ('NOT_FAILED', pgettext_lazy('Not failed', 'Not failed')),
)


class OrderSearchForm(OrderSearchFormBase):
    """
    Override form for filtering orders in dashboard.
    """

    dosimeter_serial_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Dosimeter serial number", "Dosimeter serial number"))
    owner_id = forms.IntegerField(
        required=False,
        label=pgettext_lazy("Owner", "Owner"))
    partner_id = forms.IntegerField(
        required=False,
        label=pgettext_lazy("Partner ID", "Partner ID"))
    partner_order_id = forms.IntegerField(
        required=False,
        label=pgettext_lazy("Partner Order ID", "Partner Order ID"))
    email = forms.EmailField(
        required=False,
        label=pgettext_lazy("Customer e-mail address", "Customer e-mail address"))
    address = forms.CharField(
        required=False,
        label=pgettext_lazy("Address", "Address"))
    phone_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Phone number", "Phone number"))
    approval_status = forms.ChoiceField(
        required=False,
        choices=APPROVAL_STATUS_CHOICES,
        initial='does_not_matter',
        label=pgettext_lazy("Approval status", "Approval status"))
    report_status = forms.ChoiceField(
        required=False,
        choices=REPORT_STATUS_CHOICES,
        initial='does_not_matter',
        label=pgettext_lazy("Report status", "Report status"))
    analysis_status = forms.ChoiceField(
        required=False,
        choices=ANALYSIS_STATUS_CHOICES,
        initial='does_not_matter',
        label=pgettext_lazy("Analysis status", "Analysis status"))
    weirdness_status = forms.ChoiceField(
        required=False,
        choices=WEIRDNESS_STATUS_CHOICES,
        initial='does_not_matter',
        label=pgettext_lazy("Suspect results status", "Suspect results status"))
    order_status = forms.ChoiceField(
        required=False,
        choices=ORDER_STATUS_CHOICES,
        initial='does_not_matter',
        label=pgettext_lazy("Order status", "Order status"))
    shipment_status = forms.ChoiceField(
        required=False,
        choices=SHIPMENT_STATUS_CHOICES,
        initial='does_not_matter',
        label=pgettext_lazy("Shipment status", "Shipment status"))
    is_exists_accounting = forms.NullBooleanField(
        required=False,
        label=pgettext_lazy("Is exists in accounting", "Is exists in accounting"))
    is_paid = forms.NullBooleanField(
        required=False,
        label=pgettext_lazy("Is paid", "Is paid"))
    status = None

    field_order = [
        'order_number',
        'name',
        'email',
        'address',
        'phone_number',
        'dosimeter_serial_number',
        'owner_id',
        'partner_id',
        'partner_order_id',
        'approval_status',
        'report_status',
        'analysis_status',
        'weirdness_status',
        'order_status',
        'shipment_status',
        'is_exists_accounting',
        'is_paid',
    ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) <= 4:
            return ''
        else:
            try:
                PhoneNumberValidator()(phone_number)
            except ValidationError:
                self.errors.update({'phone_number': [PhoneNumberValidator.message]})
            return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner_id'].widget.attrs.update({
            'class': 'select2 js-owner-select',
            'data-ajax-url': reverse('api:owners:owner-list'),
            'data-name': "true",
        })
        self.fields['partner_id'].widget.attrs.update({
            'class': 'select2 js-owner-select',
            'data-ajax-url': reverse('api:partners:partner-list'),
            'data-name': "true",
        })
