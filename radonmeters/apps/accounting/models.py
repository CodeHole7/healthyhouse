from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from oscar.core.loading import get_model

Order = get_model('order', 'Order')


class Accounting(models.Model):
    client_username = models.CharField(_('Client Username'), max_length=255)
    client_password = models.CharField(_('Client Password'), max_length=255)

    username = models.CharField(_('Username'), max_length=255)
    password = models.CharField(_('Password'), max_length=255)
    organization_id = models.CharField(_('Organization id'), max_length=255)
    meta_fields = JSONField(_('Meta fields'), blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Accounting'


class AccountingLedgerItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='accounting_ledgers')
    external_id = models.CharField(max_length=255)
    metadata = JSONField(_('Meta fields'), blank=True, null=True)

    class Meta:
        ordering = ('-created', )
