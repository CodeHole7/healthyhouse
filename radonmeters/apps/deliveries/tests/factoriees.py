import factory

from oscar.test.factories.order import OrderFactory
from deliveries.models import Shipment


class ShipmentFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    data = {}

    class Meta:
        model = Shipment
