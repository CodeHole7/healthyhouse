from django.test import TestCase, override_settings
from oscar.core.loading import get_model
from oscar.test.factories.order import OrderFactory, OrderLineFactory

from catalogue.tests.factories import DosimeterFactory

Dosimeter = get_model('catalogue', 'Dosimeter')


@override_settings(CELERY_ALWAYS_EAGER=True)
class OrderSignalTestCase(TestCase):

    def test_status_delivery_to_client(self):
        order_1 = OrderFactory()

        line_1 = OrderLineFactory(order=order_1)
        # serial_number should be unique
        d1 = DosimeterFactory(line=line_1, serial_number='1044')
        d2 = DosimeterFactory(line=line_1, serial_number='1045')

        d1.status = Dosimeter.STATUS_CHOICES.on_store_side
        d1.save()
        order_1.refresh_from_db()
        self.assertNotEqual(order_1.status, 'delivery_to_client')

        d2.status = Dosimeter.STATUS_CHOICES.on_store_side
        d2.save()
        order_1.refresh_from_db()
        self.assertEqual(order_1.status, 'delivery_to_client')

    def test_status_completed(self):
        order_1 = OrderFactory()

        line_1 = OrderLineFactory(order=order_1)
        # serial_number should be unique
        d1 = DosimeterFactory(line=line_1, serial_number='1044')
        d2 = DosimeterFactory(line=line_1, serial_number='1045')
        d3 = DosimeterFactory(line=line_1, serial_number='1046')

        d1.status = Dosimeter.STATUS_CHOICES.completed
        d1.save()
        order_1.refresh_from_db()
        self.assertNotEqual(order_1.status, 'completed')

        d2.status = Dosimeter.STATUS_CHOICES.on_store_side
        d2.save()
        order_1.refresh_from_db()
        self.assertNotEqual(order_1.status, 'completed')

        d3.status = Dosimeter.STATUS_CHOICES.completed
        d3.save()
        order_1.refresh_from_db()
        self.assertNotEqual(order_1.status, 'completed')

        d2.status = Dosimeter.STATUS_CHOICES.on_lab_side
        d2.save()
        order_1.refresh_from_db()
        self.assertNotEqual(order_1.status, 'completed')

        d2.status = Dosimeter.STATUS_CHOICES.completed
        d2.save()
        order_1.refresh_from_db()
        self.assertEqual(order_1.status, 'completed')
