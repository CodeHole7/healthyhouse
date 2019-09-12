import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls.base import reverse
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView
from oscar.apps.checkout.views import \
    PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.checkout.views import PaymentError, RedirectRequired
from oscar.apps.checkout.views import \
    ShippingAddressView as CoreShippingAddressView
from oscar.apps.checkout.views import UnableToTakePayment
from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from stripe import error as stripe_error

from checkout.forms import CheckoutGatewayForm
from common.tasks import mail_admins_task
from providers.stripe_app import stripe


from django.http import HttpResponseRedirect

import logging

"""
    @author: alex m
    @created: 2019.9.4
    @desc: stripe upgrade
"""
from django.http import JsonResponse

BillingAddress = get_model('order', 'BillingAddress')
from oscar.apps.checkout import exceptions

class IndexView(FormView):
    template_name = 'checkout/gateway.html'
    form_class = CheckoutGatewayForm

    def dispatch(self, request, *args, **kwargs):
        """
        Checks that user is not authenticated.
        """

        if request.user.is_authenticated:
            return redirect(reverse('checkout:shipping-address'))
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Returns redirect to different pages, based on actions of user.
        """

        # Response for customers.
        if form.cleaned_data['user_type'] == \
                CheckoutGatewayForm.TYPE_CHOICES.customer:

            # Create a message.
            messages.warning(
                request=self.request,
                message=_(
                    'Log in to your account and then you will be '
                    'redirected back to the checkout process.'))

            # Generate an URL.
            url = '{base_url}?next={next_url}'.format(
                base_url=reverse('customer:login'),
                next_url=reverse('checkout:shipping-address'))

            # Redirect to prepared URL.
            return redirect(url)

        # Response for guests.
        elif form.cleaned_data['user_type'] == \
                CheckoutGatewayForm.TYPE_CHOICES.guest:

            # Create a message.
            messages.warning(
                request=self.request,
                message=_(
                    'You will be registered automatically.'
                    'Password will be generated and sent you by email.'))

            # Generate an URL.
            url = reverse('checkout:shipping-address')

            # Redirect to prepared URL.
            return redirect(url)

        # Raise an error, for blocking magic behavior,
        # if CheckoutGatewayForm.TYPE_CHOICES will be changed.
        else:
            raise NotImplementedError


class ShippingAddressView(CoreShippingAddressView):
    """
    Overrides default behavior, for providing opportunity to sign up,
    right in the checkout's flow, just by use email address.
    """

    def check_user_email_is_captured(self, request):
        """
        Overrides default behavior for auto-passing first step `IndexView`.
        Without it cycle redirect will be started.
        """
        return

    def get_form(self, form_class=None):
        """
        Overrides default behavior for adding `request` into form args.
        """

        if form_class is None:
            form_class = self.get_form_class()

        return form_class(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        """
        Overrides default behavior for log in user,
        when him is not authenticated.
        """

        # Log in user into system, when him is not authenticated.
        if not self.request.user.is_authenticated:
            email = form.cleaned_data['email']
            user = get_user_model().objects.get(email=email)
            login(self.request, user, backend=settings.AUTHENTICATION_BACKENDS[0])

        return super().form_valid(form)


"""
    @author: alex m
    @created: 2019.9.3
    @desc: upgrade stripe for SCA
"""

def stripe_client_secret(request, secret):
    return JsonResponse({
                  'requires_action': True,
                  'payment_intent_client_secret': secret,
                  'redirect_url': reverse('checkout:thank-you')
            })
def stripe_error_return(request, error_code):
    return JsonResponse({'error':True, 'message':error_code})

class PaymentDetailsView(CorePaymentDetailsView):
    """
        Overrides default behavior for provide payment flow.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_pk'] = settings.STRIPE_PK

        # Try to get and set `card_data`. 
        source_data = self.checkout_session.payment_method()
        if source_data and isinstance(source_data, dict):
            context['card_data'] = source_data.get('card')
            

        return context

    def handle_payment_details_submission(self, request):
        # Prepare data
        try:
            source_data = json.loads(request.POST.get('payment_method'))
            card_data = source_data['card']

        except (TypeError, KeyError):
            messages.error(request, _('Invalid card data.'))
            return redirect('checkout:payment-details')
        else:
            # Set `source_data` into `checkout_session`.
            self.checkout_session.pay_by(source_data)

            # Return to default flow, with passed `card_data`.
            return self.render_preview(request, card_data=card_data)


    def handle_payment(self, order_number, total, **kwargs):
        """
            @author: alex m
            @created: 2019.9.3
            @desc: upgrade stripe for SCA
        """

        # Prepare data for creating a Payment Intent obj.

    
        try:

            if not kwargs['confirmed_payment']:
                amount = round(total.incl_tax * 100)
                currency = total.currency
                source = self.checkout_session.payment_method().get('id')
                metadata = {'order_id': order_number}
                    
                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency=currency,
                    description="Charge for order: %s." % order_number,
                    payment_method=source,
                    confirmation_method='manual',
                    confirm=True,
                    metadata=metadata)
            else:
                intent = stripe.PaymentIntent.confirm(kwargs['confirmed_payment'])
                

            if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
                #self.restore_frozen_basket()
                # Tell the client to handle the action
                raise RedirectRequired(reverse('checkout:stripe_client_secret', args=[intent.client_secret]))


            elif intent.status == 'succeeded':
                # The payment didn’t need any additional actions and completed!
                # Handle post-payment fulfillment

                mail_admins_task.delay(
                subject='Stripe: StripeCharge was created.',
                message='ID of intent: %s' % intent.id)

            else:

                self.restore_frozen_basket()
                # Invalid status
                raise RedirectRequired(reverse('checkout:stripe_error_return', args=['UnkownError']))

        except stripe_error.CardError as e:
            # Prepare error message.
            msg = str(e)
            # Notify admins about error. 
            mail_admins_task.delay(
                subject='Stripe: CardError was raised.',
                message='Original response:\n%s' % msg)
            #return JsonResponse({'error': 'Original response:\n%s' % msg}, status_code=500)
            # Raise error.
            self.restore_frozen_basket()
            # Invalid status
            raise RedirectRequired(reverse('checkout:stripe_error_return', args=['CardError']))

        except stripe_error.StripeError as e:
            # Prepare error message.
            msg = str(e)

            # Notify admins about error.
            mail_admins_task.delay(
                subject='Stripe: StripeError was raised.',
                message='Original response:\n%s' % msg)
            #return JsonResponse({'error': 'Original response:\n%s' % msg}, status_code=500)
            # Raise error.
            self.restore_frozen_basket()
            # Invalid status
            raise RedirectRequired(reverse('checkout:stripe_error_return', args=['StripeError']))
          

    def handle_successful_order(self, order):
        """

        @author: alex m
        @created: 2019.9.6
        @desc: upgrade for SCA

        Handle the various steps required after an order has been successfully
        placed.

        Override this view if you want to perform custom actions when an
        order is submitted.

        """
        # Send confirmation message (normally an email)
        self.send_confirmation_message(order, self.communication_type_code)

        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id

        success_url = self.get_success_url()
        response = HttpResponseRedirect(success_url)

        self.send_signal(self.request, response, order)

        return JsonResponse({
              'success_url': success_url,
        })

    def submit(self, user, basket, **kwargs):

        """
        Overridden for adding validation on quantity.
        """

        # Validation for handling cases, when user change the form data manually
        # and tries to order some product with quantity less than it possible.
        # For each line (product) will be generated error messages.
        
        invalid_lines = False
        for l in basket.lines.all():
            if l.quantity < l.product.min_num_for_order:
                invalid_lines = True
                msg = _('Minimum quantity for ordering "{product}" is {count}.').format(
                    product=l.product.get_title(),
                    count=l.product.min_num_for_order)
                messages.error(self.request, msg)

        # Redirect to current page, when basket has invalid lines.
        if invalid_lines:
            return redirect(reverse('checkout:preview'))

        # Set billing address if user set any in address book
        default_billing_address = user.addresses.filter(is_default_for_billing=True).first()
        if default_billing_address:
            billing_address = BillingAddress()
            default_billing_address.populate_alternative_model(billing_address)
            kwargs.update({'billing_address': billing_address})



        # Return to default implementation.
        return super().submit(user, basket, **kwargs)

    def handle_place_order_submission(self, request):
        """
    
        @author: alex m
        @created: 2019.9.6
        @desc: upgrade for SCA

        Handle a request to place an order.
        This method is normally called after the customer has clicked "place
        order" on the preview page. It's responsible for (re-)validating any
        form information then building the submission dict to pass to the
        `submit` method.
        If forms are submitted on your payment details view, you should
        override this method to ensure they are valid before extracting their
        data into the submission dict and passing it onto `submit`.
        """

        payment_kwargs = {'confirmed_payment':request.POST.get('payment_intent_id', False)}

        return self.submit(**self.build_submission(payment_kwargs= payment_kwargs))

    def check_basket_is_not_empty(self, request):

        if request.POST.get('error', False):
            self.restore_frozen_basket()
            raise exceptions.FailedPreCondition(
                url=reverse('basket:summary'),
                message=_(
                    "No paid")
            )

        if request.POST.get('payment_intent_id', False):
            self.restore_frozen_basket()

        if request.basket.is_empty:
            raise exceptions.FailedPreCondition(
                url=reverse('basket:summary'),
                message=_(
                    "You need to add some items to your basket to checkout")
            )


