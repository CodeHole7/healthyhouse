# Create your models here.
import datetime

from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from oscar.core.loading import get_model

from common.models import UUIDAbstractModel


Order = get_model('order', 'Order')


class AbstractShipment(UUIDAbstractModel, TimeStampedModel):
    """
    Model for storing Shipment details.

    `data` field example:
    {
        "id": 1168,
        "created_at": "2017-06-16T08:25:44.557+02:00",
        "updated_at": "2017-06-16T08:25:44.557+02:00",
        "carrier_code": "gls",
        "description": "Til Pakkeshop 5,0 kg",
        "product_id": 64,
        "services": "23, 24",
        "product_code": "GLSDK_SD",
        "service_codes": "EMAIL_NT,SMS_NT",
        "price": "42.5",
        "reference": "Webshop 5678",
        "order_id": "1000002345",
        "pkg_no": "6064518784",
        "receiver": {
            "name": "Lene Jensen",
            "attention": None,
            "address1": "Vindegade 112",
            "address2": None,
            "zipcode": "5000",
            "city": "Odense C",
            "country_code": "DK",
            "email": "lene@email.dk",
            "mobile": "50607080",
            "telephone": "50607080",
            "instruction": None
        },
        "sender": {
            "name": "Pakkelabels.dk ApS",
            "attention": None,
            "address1": "Strandvejen 6",
            "address2": None,
            "zipcode": "5240",
            "city": "Odense NØ",
            "country_code": "DK",
            "email": "firma@email.dk",
            "mobile": "70400407",
            "telephone": "70400407"
        },
        "service_point": {
            "id": "95558",
            "name": "Påskeløkkens Købmand",
            "address1": "Paaskeløkkevej 11",
            "address2": None,
            "zipcode": "5000",
            "city": "Odense C",
            "country": "DK"
        },
        "pick_up": {}
    }

    Status fields examples:
        current_status: "EN_ROUTE"
        current_status_text: "Forsendelsen er ankommet til distributionscenter"
        current_status_registered_at: 2017-06-16T08:25:44.557+02:00
    """

    data = JSONField(
        verbose_name=_('Data'))
    current_status = models.CharField(blank=True, max_length=25)
    current_status_text = models.CharField(blank=True, max_length=255)
    current_status_registered_at = models.DateTimeField(blank=True, null=True)
    order = models.OneToOneField(
        to=Order,
        verbose_name=_('Order'))

    class Meta:
        ordering = ('-created',)
        abstract = True

    def days_to_pick_up(self):
        if self.current_status != 'AVAILABLE_FOR_DELIVERY':
            return 0
        remaining_time = self.current_status_registered_at + datetime.timedelta(days=14) - timezone.now()
        return remaining_time.days

    def __str__(self):
        if self.data:
            return str(self.data.get('id'))
        else:
            return str(self.pk)


class Shipment(AbstractShipment):
    """
    Main model for storing ReturnLabel details.
    """

    class Meta:
        default_related_name = 'shipment'


class ShipmentReturn(AbstractShipment):
    """
    Model for storing ReturnLabel details.
    WARNING
    We use separate model instead of Shipment for being sure
    that relation order OneToOneField will be consistent.
    """

    class Meta:
        default_related_name = 'shipment_return'


class ShipmentLabel(UUIDAbstractModel, TimeStampedModel):
    """
    Model for storing Label details.
    """

    order = models.OneToOneField(
        to=Order,
        related_name='label',
        verbose_name=_('Label'))
    number = models.CharField(
        verbose_name=_('Label number'),
        max_length=255, blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.number
