from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from oscar.test.factories.order import OrderFactory, OrderLineFactory

from catalogue.tests.factories import DosimeterFactory
from common.models import DosimeterPDFReportTheme
from common.tests.factories import DosimeterPDFReportThemeFactory
from owners.tests.factories import OwnerFactory


class DosimeterPDFReportThemeSelectTheme(TestCase):

    def test_get_theme(self):
        owner_1 = OwnerFactory()
        owner_2 = OwnerFactory()

        t1 = DosimeterPDFReportThemeFactory(
            owner=owner_1,
            min_concentration=0,
            max_concentration=50)
        t2 = DosimeterPDFReportThemeFactory(
            owner=owner_1,
            min_concentration=50,
            max_concentration=100)
        t3 = DosimeterPDFReportThemeFactory(
            owner=owner_2,
            min_concentration=50,
            max_concentration=100)

        date_start = timezone.now()
        date_end = date_start + timedelta(days=2)

        # dosimeters_avg_concentration
        # 44.64
        order_1 = OrderFactory(owner=owner_1)
        line_1 = OrderLineFactory(order=order_1)
        d1_1 = DosimeterFactory(
            line=line_1,
            concentration=5,
            uncertainty=5,
            measurement_start_date=date_start,
            measurement_end_date=date_end)
        d1_2 = DosimeterFactory(
            line=line_1,
            concentration=10,
            uncertainty=10,
            measurement_start_date=date_start,
            measurement_end_date=date_end)

        # dosimeters_avg_concentration
        # 59.52
        order_2 = OrderFactory(owner=owner_2)
        line_2 = OrderLineFactory(order=order_2)
        d2_1 = DosimeterFactory(
            line=line_2,
            concentration=5,
            uncertainty=5,
            measurement_start_date=date_start,
            measurement_end_date=date_end)
        d2_2 = DosimeterFactory(
            line=line_2,
            concentration=10,
            uncertainty=10,
            measurement_start_date=date_start,
            measurement_end_date=date_end)

        theme = DosimeterPDFReportTheme.get_theme(order_1)
        self.assertEqual(theme, t1)

        theme = DosimeterPDFReportTheme.get_theme(order_2)
        self.assertEqual(theme, None)

        d1_1.concentration = 10
        d1_1.uncertainty = 10
        d1_1.save()
        d2_1.concentration = 10
        d2_1.uncertainty = 10
        d2_1.save()
        del order_1.dosimeters_avg_concentration
        del order_2.dosimeters_avg_concentration

        theme = DosimeterPDFReportTheme.get_theme(order_1)
        self.assertEqual(theme, t2)

        theme = DosimeterPDFReportTheme.get_theme(order_2)
        self.assertEqual(theme, t3)

        d1_1.concentration = 50
        d1_1.uncertainty = 50
        d1_1.save()
        d2_1.concentration = 50
        d2_1.uncertainty = 50
        d2_1.save()

        del order_1.dosimeters_avg_concentration
        del order_2.dosimeters_avg_concentration

        theme = DosimeterPDFReportTheme.get_theme(order_1)
        self.assertEqual(theme, None)

        theme = DosimeterPDFReportTheme.get_theme(order_2)
        self.assertEqual(theme, None)
