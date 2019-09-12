from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from oscar.core.loading import get_model
from stripe.error import InvalidRequestError

from common.models import UUIDAbstractModel
from common.tasks import mail_admins_task
from providers.stripe_app import stripe

Order = get_model('order', 'Order')


class StripeAbstractModel(
        UUIDAbstractModel,
        TimeStampedModel):
    """
    Abstract model for stripe objects.
    """
    stripe_id = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.pk)

    @cached_property
    def _stripe_type(self):
        return self._meta.model.__name__.replace('Stripe', '')


class StripeCharge(StripeAbstractModel):
    """
    Model for saving Stripe Charges.

    Stripe doc:
    https://stripe.com/docs/api/python#charges
    """
    metadata = JSONField(_('Metadata'), default=dict, blank=True)
    order = models.OneToOneField(
        Order,
        related_name='stripe_charge',
        verbose_name=_('Order'))

    @cached_property
    def stripe_obj(self):
        try:
            return stripe.Charge.retrieve(self.stripe_id)
        except InvalidRequestError as e:
            mail_admins_task.delay(
                subject='Stripe: System cannot retrieve StripeCharge.',
                message='Original response:\n%s' % str(e))
            return

    @cached_property
    def stripe_dashboard_url(self):
        if 'pk_test_' in settings.STRIPE_PK:
            base_url = 'https://dashboard.stripe.com/test/payments/'
        else:
            base_url = 'https://dashboard.stripe.com/payments/'
        return '%s%s' % (base_url, self.stripe_id)

    def apply_capture(self):
        """
        Method for applying captures.
        """
        # Make an action.
        self.stripe_obj.capture()

        # Update instance.
        self.metadata = self.stripe_obj.to_dict()
        self.save()

    def apply_refund(self, amount):
        """
        Method for applying refunds.
        """
        # Make an action.
        stripe.Refund.create(
            amount=amount,
            charge=self.stripe_id,
            reverse_transfer=True)

        # Update instance.
        self.metadata = self.stripe_obj.to_dict()
        self.save()
