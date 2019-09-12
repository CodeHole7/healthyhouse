from uuid import uuid4

from django.contrib import messages
from django.db import IntegrityError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.views.generic import FormView
from oscar.core.loading import get_class
from oscar.core.loading import get_model

VoucherBulkCreateForm = get_class(
    'dashboard.vouchers.forms',
    'VoucherBulkCreateForm')
VoucherSendEmailForm = get_class(
    'dashboard.vouchers.forms',
    'VoucherSendEmailForm')

Voucher = get_model('voucher', 'Voucher')
ConditionalOffer = get_model('offer', 'ConditionalOffer')
Benefit = get_model('offer', 'Benefit')
Condition = get_model('offer', 'Condition')


class VoucherBulkCreateView(FormView):
    """
    View for generating many vouchers by one request.
    """

    form_class = VoucherBulkCreateForm
    template_name = 'dashboard/vouchers/voucher_bulk_create_form.html'
    success_url = reverse_lazy('dashboard:voucher-list')

    @transaction.atomic()
    def form_valid(self, form):

        # Create condition.
        condition = Condition.objects.create(
            range=form.cleaned_data['benefit_range'],
            type=Condition.COUNT,
            value=1)

        # Create benefit.
        benefit = Benefit.objects.create(
            range=form.cleaned_data['benefit_range'],
            type=form.cleaned_data['benefit_type'],
            value=form.cleaned_data['benefit_value'])

        # Prepare name for ConditionalOffer.
        name = _("Offer for vouchers group: '{name}' [benefit id: {id}]".format(
            name=form.cleaned_data['name'],
            id=benefit.id))

        # Create offer.
        offer = ConditionalOffer.objects.create(
            name=name,
            offer_type=ConditionalOffer.VOUCHER,
            benefit=benefit,
            condition=condition)

        # Bulk create vouchers.
        quantity = form.cleaned_data['quantity']
        for i in range(quantity):

            while True:
                # Create a voucher.
                try:
                    # Needed for natural handling of integrity errors:
                    with transaction.atomic():
                        voucher = Voucher.objects.create(
                            code=uuid4().hex.upper()[:10],
                            name=form.cleaned_data['name'],
                            usage=form.cleaned_data['usage'],
                            start_datetime=form.cleaned_data['start_datetime'],
                            end_datetime=form.cleaned_data['end_datetime'])
                # Try again.
                except IntegrityError:
                    continue
                # Attach a voucher to offer and go to next iteration.
                else:
                    voucher.offers.add(offer)
                    break

        # Create a message for admin.
        msg = ungettext(
            '%(count)d Coupon has been created.',
            '%(count)d Coupons have been created.', quantity
        ) % {'count': quantity}
        messages.success(request=self.request, message=msg)

        # Redirect user to the main page of this section.
        return HttpResponseRedirect(self.get_success_url())


class VoucherSendEmailView(FormView):
    """
    View for sending vouchers to users (or email addresses) via email.
    """

    form_class = VoucherSendEmailForm
    template_name = 'dashboard/vouchers/send_voucher_email.html'
    success_url = reverse_lazy('dashboard:send-voucher')

    def form_valid(self, form):
        """
        Overridden for generating message for admin.
        """

        # Create a message for admin.
        user = form.cleaned_data.get('user')
        email = form.cleaned_data.get('email')
        target = user.email if user else email
        messages.success(
            request=self.request,
            message=_('Voucher was successfully sent to "%s".') % target)

        return super().form_valid(form)
