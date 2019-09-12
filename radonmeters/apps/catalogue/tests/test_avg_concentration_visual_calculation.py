from datetime import timedelta, datetime

from django.test import TestCase
from django.utils import timezone
from oscar.core.loading import get_model
from oscar.test.factories.order import OrderLineFactory

from catalogue.tests.factories import DosimeterFactory

Partner = get_model('partner', 'Partner')
Country = get_model('address', 'Country')
ShippingAddress = get_model('order', 'ShippingAddress')
BillingAddress = get_model('order', 'BillingAddress')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
Product = get_model('catalogue', 'Product')
Dosimeter = get_model('catalogue', 'Dosimeter')
DefaultProduct = get_model('catalogue', 'DefaultProduct')


class DosimeterCalculationTestCase(TestCase):

    def setUp(self):
        super().setUp()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line = OrderLineFactory()

    def test_calculation(self):
        line = self.line
        date_start = timezone.now()
        date_end = date_start + timedelta(days=2)

        d_1 = DosimeterFactory(
            line=line,
            active_area=False, floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=120)
        d_2 = DosimeterFactory(
            line=line,
            active_area=True, floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=110)
        d_3 = DosimeterFactory(
            line=line,
            active_area=True, floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=100)

        # print('d1', d_1.concentration_visual)
        # print('d2', d_2.concentration_visual)
        # print('d3', d_3.concentration_visual)

        self.assertEqual(d_1.avg_concentration_visual, 625.0)

        d_1.active_area = True
        d_1.save()
        self.assertEqual(d_1.avg_concentration_visual, 654.76)

        d_1.floor = 0
        d_1.save()
        self.assertEqual(d_1.avg_concentration_visual, 669.64)

    def test_calculation_is_active(self):
        line = self.line
        date_start = timezone.now()
        date_end = date_start + timedelta(days=2)

        d_1 = DosimeterFactory(
            line=line,
            floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            uncertainty=10,
            concentration=120)
        d_2 = DosimeterFactory(
            line=line,
            floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            is_active=False,
            uncertainty=10,
            concentration=110)
        d_3 = DosimeterFactory(
            line=line,
            floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            is_active=False,
            uncertainty=10,
            concentration=100)

        # print('d1', d_1.concentration_visual)
        # print('d2', d_2.concentration_visual)
        # print('d3', d_3.concentration_visual)

        line.refresh_from_db()
        self.assertNotEqual(d_1.avg_concentration_visual, 625.0)
        self.assertEqual(d_1.avg_concentration_visual, d_1.concentration_visual)
        self.assertEqual(line.order.dosimeters_pdf_report_can_be_generated, True)

        d_1.is_active = False
        d_1.save()
        line.refresh_from_db()
        self.assertEqual(line.order.dosimeters_pdf_report_can_be_generated, False)
        self.assertEqual(d_1.avg_concentration_visual, None)

        d_1.is_active = True
        d_1.save()
        d_2.is_active = True
        d_2.save()
        line.refresh_from_db()
        self.assertEqual(line.order.dosimeters_pdf_report_can_be_generated, True)
        v = (d_1.concentration_visual + d_2.concentration_visual) / 2
        self.assertEqual(d_1.avg_concentration_visual, round(v, 2))

    def test_calculation_days(self):
        line = self.line
        date_start = datetime(year=2017, month=12, day=18)
        date_end = datetime(year=2018, month=3, day=2)

        d_1 = DosimeterFactory(
            line=line,
            active_area=True, floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=600.288)
        d_2 = DosimeterFactory(
            line=line,
            active_area=True, floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=562.992)

        self.assertEqual(d_1.measurement_days, 74)
        self.assertEqual(d_1.concentration_visual, 338)

    def test_raw_concentration(self):
        line = self.line
        date_start = timezone.now()
        date_end = date_start + timedelta(days=2)

        d_1 = DosimeterFactory(
            line=line,
            active_area=True, floor=-1,
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=120,
            uncertainty=15)

        # concentration calculate
        self.assertNotEqual(d_1.concentration_visual, d_1.concentration)
        self.assertNotEqual(d_1.uncertainty_visual, d_1.uncertainty)

        d_1.use_raw_concentration = True
        d_1.save()

        self.assertEqual(d_1.concentration_visual, d_1.concentration)
        self.assertEqual(d_1.uncertainty_visual, d_1.uncertainty)
