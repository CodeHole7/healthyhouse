from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from oscar.test.factories import UserFactory
from oscar.test.factories.order import OrderFactory, OrderLineFactory, ShippingAddressFactory, BillingAddressFactory
from oscar.test.factories.partner import PartnerFactory
from rest_framework import status

from owners.tests.factories import OwnerFactory
from catalogue.tests.factories import DosimeterFactory


class OrderSearchTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory(is_superuser=True, is_staff=True)

        cls.url_order_list = reverse('dashboard:order-list')

    def test_list_search(self):
        self.client.force_login(self.admin)
        owner_1 = OwnerFactory()
        owner_2 = OwnerFactory()

        order_1 = OrderFactory(owner=owner_1)
        order_2 = OrderFactory(owner=owner_2)
        order_2_1 = OrderFactory(owner=owner_2, partner_order_id='997788')

        partner_1 = PartnerFactory()
        partner_2 = PartnerFactory()

        line_1 = OrderLineFactory(order=order_1, partner=partner_1)
        # serial_number should be unique
        DosimeterFactory(line=line_1, serial_number='1044')
        DosimeterFactory(line=line_1, serial_number='1045')

        line_2 = OrderLineFactory(order=order_2, partner=partner_1)
        DosimeterFactory(line=line_2, serial_number='1048')
        DosimeterFactory(line=line_2, serial_number='1146')

        line_2_1 = OrderLineFactory(order=order_2_1, partner=partner_2)

        scenario = [
            # dosimeter number
            {'data': {'dosimeter_serial_number': '1044'},
             'results': [order_1]},
            {'data': {'dosimeter_serial_number': '1045'},
             'results': [order_1]},
            {'data': {'dosimeter_serial_number': '1146'},
             'results': [order_2]},

            # owner
            {'data': {'owner_id': owner_1.id},
             'results': [order_1]},
            {'data': {'owner_id': owner_2.id},
             'results': [order_2_1, order_2]},

            # partner
            {'data': {'partner_id': partner_1.id},
             'results': [order_2, order_1]},
            {'data': {'partner_id': partner_2.id},
             'results': [order_2_1]},

            # partner order id
            {'data': {'partner_order_id': order_2_1.partner_order_id},
             'results': [order_2_1]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_user_search(self):
        self.client.force_login(self.admin)

        user_1 = UserFactory(first_name='Eva Maria', last_name='Smith', email='eva@example.com')
        user_2 = UserFactory(first_name='Jan', last_name='Møller Holm', email='jan@test.org', phone_number='+4520316479')
        order_1 = OrderFactory(user=user_1)
        order_2 = OrderFactory(user=user_2)

        line_1 = OrderLineFactory(order=order_1)
        line_2 = OrderLineFactory(order=order_2)

        scenario = [
            {'data': {'name': 'Jan'},
             'results': [order_2]},
            {'data': {'name': 'Holm'},
             'results': [order_2]},
            {'data': {'name': 'Møller Holm'},
             'results': [order_2]},
            {'data': {'name': 'Møller'},
             'results': [order_2]},
            {'data': {'name': 'Jan Møller Holm'},
             'results': [order_2]},
            {'data': {'name': 'Jan Smith'},
             'results': [order_2, order_1]},
            {'data': {'name': 'Eva'},
             'results': [order_1]},
            {'data': {'name': 'Eva Maria'},
             'results': [order_1]},
            {'data': {'name': 'Maria'},
             'results': [order_1]},
            {'data': {'email': 'eva@example.com'},
             'results': [order_1]},
            {'data': {'email': 'EVA@ExampLe.com'},
             'results': [order_1]},
            {'data': {'email': 'something@example.com'},
             'results': []},
            {'data': {'email': 'jan@test.org'},
             'results': [order_2]},
            {'data': {'phone_number': '+4520316479'},
             'results': [order_2]},
            {'data': {'phone_number': '+4520316478'},
             'results': []},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_address_search(self):
        self.client.force_login(self.admin)

        address_1 = BillingAddressFactory(first_name='Eva Maria', last_name='Smith', line1='1 King Road', line4 = "London")
        address_2 = ShippingAddressFactory(first_name='Jan', last_name='Møller Holm', line1='2 Queen Line', line4 = "london")
        order_1 = OrderFactory(billing_address=address_1)
        order_2 = OrderFactory(shipping_address=address_2)

        scenario = [
            {'data': {'address': 'Jan'},
             'results': [order_2]},
            {'data': {'address': 'Holm'},
             'results': [order_2]},
            {'data': {'address': 'Møller Holm'},
             'results': [order_2]},
            {'data': {'address': 'Møller'},
             'results': [order_2]},
            {'data': {'address': 'Jan Møller Holm'},
             'results': [order_2]},
            {'data': {'address': 'London'},
             'results': [order_2, order_1]},
            {'data': {'address': 'King'},
             'results': [order_1]},
            {'data': {'address': 'Queen'},
             'results': [order_2]},
            {'data': {'address': 'Something'},
             'results': []},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_approval_status_search(self):
        self.client.force_login(self.admin)

        order_not_approved_not_ready_1 = OrderFactory(is_approved=False)
        line_1 = OrderLineFactory(order=order_not_approved_not_ready_1)
        DosimeterFactory(line=line_1, serial_number='1044',
                         measurement_start_date=None,
                         measurement_end_date=None,
                         concentration=None,
                         location='',)

        order_not_approved_not_ready_2 = OrderFactory(is_approved=False)
        line_2 = OrderLineFactory(order=order_not_approved_not_ready_2)
        DosimeterFactory(line=line_2, serial_number='1045',
                         concentration=1.0,)
        DosimeterFactory(line=line_2, serial_number='1046',
                         concentration=0,)

        order_not_approved_not_ready_3 = OrderFactory(is_approved=False)
        line_5 = OrderLineFactory(order=order_not_approved_not_ready_3)
        DosimeterFactory(line=line_5, serial_number='1051',
                         concentration=1.0,
                         floor=None)

        order_not_approved_not_ready_4 = OrderFactory(is_approved=False)
        line_6 = OrderLineFactory(order=order_not_approved_not_ready_4)
        DosimeterFactory(line=line_6, serial_number='1052',
                         concentration=1.0,
                         uncertainty=None)

        order_not_approved_ready_1 = OrderFactory(is_approved=False)
        line_3 = OrderLineFactory(order=order_not_approved_ready_1)
        DosimeterFactory(line=line_3, serial_number='1047',
                         concentration=1.0,
                         uncertainty=1.0)
        DosimeterFactory(line=line_3, serial_number='1048',
                         concentration=2.0,
                         uncertainty=1.0)

        order_approved_ready_1 = OrderFactory(is_approved=True)
        line_4 = OrderLineFactory(order=order_approved_ready_1)
        DosimeterFactory(line=line_4, serial_number='1049',
                         concentration=2.0,
                         uncertainty=1.0)
        DosimeterFactory(line=line_4, serial_number='1050',
                         concentration=5.0,
                         uncertainty=1.0)

        scenario = [
            {'data': {'approval_status': 'does_not_matter'},
             'results': [order_approved_ready_1,
                         order_not_approved_ready_1,
                         order_not_approved_not_ready_4,
                         order_not_approved_not_ready_3,
                         order_not_approved_not_ready_2,
                         order_not_approved_not_ready_1]},
            {'data': {'approval_status': 'ready_for_approval_and_not_approved'},
             'results': [order_not_approved_ready_1]},
            {'data': {'approval_status': 'approved'},
             'results': [order_approved_ready_1]},
            {'data': {'approval_status': 'not_ready_for_approval_and_not_approved'},
             'results': [order_not_approved_not_ready_4,
                         order_not_approved_not_ready_3,
                         order_not_approved_not_ready_2,
                         order_not_approved_not_ready_1]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_report_status_search(self):
        self.client.force_login(self.admin)

        order_not_reported_not_sent = OrderFactory(is_reported_by_partner=False,
                                                   is_report_sent=False)
        order_not_reported_sent = OrderFactory(is_reported_by_partner=False,
                                                   is_report_sent=True)
        order_reported_not_sent = OrderFactory(is_reported_by_partner=True,
                                                   is_report_sent=False)
        order_reported_sent = OrderFactory(is_reported_by_partner=True,
                                                   is_report_sent=True)

        scenario = [
            {'data': {'report_status': 'does_not_matter'},
             'results': [order_reported_sent,
                         order_reported_not_sent,
                         order_not_reported_sent,
                         order_not_reported_not_sent]},
            {'data': {'report_status': 'sent'},
             'results': [order_reported_sent,
                         order_not_reported_sent]},
            {'data': {'report_status': 'reported'},
             'results': [order_reported_sent,
                         order_reported_not_sent]},
            {'data': {'report_status': 'not reported'},
             'results': [order_not_reported_sent,
                         order_not_reported_not_sent]},
            {'data': {'report_status': 'sent_or_reported'},
             'results': [order_reported_sent,
                         order_reported_not_sent,
                         order_not_reported_sent]},
            {'data': {'report_status': 'not_sent_and_not_reported'},
             'results': [order_not_reported_not_sent]},
            {'data': {'report_status': 'sent_and_reported'},
             'results': [order_reported_sent]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_analysis_status_search(self):
        self.client.force_login(self.admin)

        order_no_slip_no_lab = OrderFactory()
        line_1 = OrderLineFactory(order=order_no_slip_no_lab)
        DosimeterFactory(line=line_1, serial_number='1044',
                         measurement_start_date=None,
                         measurement_end_date=None,
                         location='',
                         concentration=None,)

        order_partial_slip_partial_lab = OrderFactory()
        line_2 = OrderLineFactory(order=order_partial_slip_partial_lab)
        DosimeterFactory(line=line_2, serial_number='1045',
                         measurement_start_date=None,
                         measurement_end_date=None,
                         location='',
                         concentration=1.0,)
        DosimeterFactory(line=line_2, serial_number='1046',
                         concentration=None,
                         floor=0)

        order_no_slip_lab = OrderFactory()
        line_3 = OrderLineFactory(order=order_no_slip_lab)
        DosimeterFactory(line=line_3, serial_number='1047',
                         measurement_start_date=None,
                         measurement_end_date=None,
                         location='',
                         concentration=1.0,)
        DosimeterFactory(line=line_3, serial_number='1048',
                         measurement_start_date=None,
                         measurement_end_date=None,
                         location='',
                         concentration=2.0,)

        order_slip_no_lab = OrderFactory()
        line_4 = OrderLineFactory(order=order_slip_no_lab)
        DosimeterFactory(line=line_4, serial_number='1049',
                         concentration=None,
                         floor=-1)
        DosimeterFactory(line=line_4, serial_number='1050',
                         concentration=0.0,
                         floor=3)

        order_slip_lab_no_result = OrderFactory()
        line_5 = OrderLineFactory(order=order_slip_lab_no_result)
        DosimeterFactory(line=line_5, serial_number='1051',
                         concentration=2.0,
                         floor=2)

        order_no_slip_lab_result = OrderFactory()
        line_6 = OrderLineFactory(order=order_no_slip_lab_result)
        DosimeterFactory(line=line_6, serial_number='1052',
                         concentration=2.0,
                         uncertainty=1.0,
                         measurement_start_date=None,
                         measurement_end_date=None,
                         location='',
                         floor=None)

        order_slip_lab_result = OrderFactory()
        line_7 = OrderLineFactory(order=order_slip_lab_result)
        DosimeterFactory(line=line_7, serial_number='1053',
                         concentration=2.0,
                         uncertainty=1.0,
                         floor=1)

        order_inactive = OrderFactory()
        line_8 = OrderLineFactory(order=order_inactive)
        DosimeterFactory(line=line_8, serial_number='1054',
                         concentration=2.0,
                         uncertainty=1.0,
                         floor=1,
                         is_active=False)
        DosimeterFactory(line=line_8, serial_number='1055',
                         measurement_start_date=None,
                         measurement_end_date=None,
                         location='',
                         concentration=None,
                         uncertainty=None,
                         floor=None)


        scenario = [
            {'data': {'analysis_status': 'does_not_matter'},
             'results': [order_inactive,
                         order_slip_lab_result,
                         order_no_slip_lab_result,
                         order_slip_lab_no_result,
                         order_slip_no_lab,
                         order_no_slip_lab,
                         order_partial_slip_partial_lab,
                         order_no_slip_no_lab]},
            {'data': {'analysis_status': 'no_slip_result'},
             'results': [order_no_slip_lab_result]},
            {'data': {'analysis_status': 'no_result_slip'},
             'results': [order_slip_lab_no_result,
                         order_slip_no_lab]},
            {'data': {'analysis_status': 'empty'},
             'results': [order_inactive]},
            {'data': {'analysis_status': 'partial'},
             'results': [order_no_slip_lab,
                         order_partial_slip_partial_lab,
                         order_no_slip_no_lab]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_weird_orders(self):
        self.client.force_login(self.admin)

        order_outlier = OrderFactory()
        line_1 = OrderLineFactory(order=order_outlier)
        DosimeterFactory(line=line_1, serial_number='1046',
                         concentration=120.0,
                         uncertainty=1.0,
                         floor=2,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_1, serial_number='1047',
                         concentration=10.0,
                         uncertainty=1.0,
                         floor=3,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))

        order_overlap_level_1 = OrderFactory()
        line_2 = OrderLineFactory(order=order_overlap_level_1)
        DosimeterFactory(line=line_2, serial_number='1048',
                         concentration=13.0,
                         uncertainty=1.0,
                         floor=0,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_2, serial_number='1049',
                         concentration=16.0,
                         uncertainty=1.0,
                         floor=1,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_2, serial_number='1050',
                         concentration=16.0,
                         uncertainty=1.0,
                         floor=2,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))

        order_overlap_level_2 = OrderFactory()
        line_3 = OrderLineFactory(order=order_overlap_level_2)
        DosimeterFactory(line=line_3, serial_number='1051',
                         concentration=13.0,
                         uncertainty=1.0,
                         floor=0,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_3, serial_number='1052',
                         concentration=18.0,
                         uncertainty=1.0,
                         floor=1,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_3, serial_number='1053',
                         concentration=23.0,
                         uncertainty=1.0,
                         floor=2,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))

        order_normal = OrderFactory()
        line_4 = OrderLineFactory(order=order_normal)
        DosimeterFactory(line=line_4, serial_number='1054',
                         concentration=12.1,
                         uncertainty=1.0,
                         floor=0,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_4, serial_number='1055',
                         concentration=8.0,
                         uncertainty=1.0,
                         floor=1,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_4, serial_number='1056',
                         concentration=3.0,
                         uncertainty=1.0,
                         floor=2,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))

        order_override = OrderFactory(not_weird=True)
        line_5 = OrderLineFactory(order=order_override)
        DosimeterFactory(line=line_5, serial_number='1057',
                         concentration=109,
                         uncertainty=1.0,
                         floor=0,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_5, serial_number='1058',
                         concentration=121,
                         uncertainty=1.0,
                         floor=1,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))
        DosimeterFactory(line=line_5, serial_number='1059',
                         concentration=600,
                         uncertainty=1.0,
                         floor=2,
                         measurement_start_date = timezone.now().date(),
                         measurement_end_date = timezone.now().date() + timezone.timedelta(days=41))

        order_override.update_weirdness_statuses()
        order_normal.update_weirdness_statuses()
        order_outlier.update_weirdness_statuses()
        order_overlap_level_1.update_weirdness_statuses()
        order_overlap_level_2.update_weirdness_statuses()
        order_override.save()
        order_normal.save()
        order_outlier.save()
        order_overlap_level_1.save()
        order_overlap_level_2.save()

        scenario = [
            {'data': {'weirdness_status': 'does_not_matter'},
             'results': [order_override,
                         order_normal,
                         order_overlap_level_2,
                         order_overlap_level_1,
                         order_outlier]},
            {'data': {'weirdness_status': 'outlier'},
             'results': [order_outlier]},
            {'data': {'weirdness_status': 'level_1_overlap'},
             'results': [order_override,
                         order_overlap_level_2,
                         order_overlap_level_1]},
            {'data': {'weirdness_status': 'level_2_overlap'},
             'results': [order_override,
                         order_overlap_level_2]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_order_status_search(self):
        self.client.force_login(self.admin)

        order_created = OrderFactory(status='created')
        order_issued = OrderFactory(status='issued')
        order_delivery_to_client = OrderFactory(status='delivery_to_client')
        order_completed = OrderFactory(status='completed')
        order_canceled = OrderFactory(status='canceled')

        scenario = [
            {'data': {'order_status': 'does_not_matter'},
             'results': [order_canceled,
                         order_completed,
                         order_delivery_to_client,
                         order_issued,
                         order_created]},
            {'data': {'order_status': 'not canceled'},
             'results': [order_completed,
                         order_delivery_to_client,
                         order_issued,
                         order_created]},
            {'data': {'order_status': 'created'},
             'results': [order_created]},
            {'data': {'order_status': 'issued'},
             'results': [order_issued]},
            {'data': {'order_status': 'delivery_to_client'},
             'results': [order_delivery_to_client]},
            {'data': {'order_status': 'completed'},
             'results': [order_completed]},
            {'data': {'order_status': 'canceled'},
             'results': [order_canceled]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)

    def test_order_account_system(self):
        self.client.force_login(self.admin)

        order_not_paid_exist = OrderFactory(is_exists_accounting=True, is_paid=False)
        order_not_paid_not_exist = OrderFactory(is_exists_accounting=False, is_paid=False)
        order_paid_not_exist = OrderFactory(is_exists_accounting=False, is_paid=True)
        order_paid_exist = OrderFactory(is_exists_accounting=True, is_paid=True)

        scenario = [
            {'data': {'is_exists_accounting': None, 'is_paid': None},
             'results': [order_paid_exist,
                         order_paid_not_exist,
                         order_not_paid_not_exist,
                         order_not_paid_exist]},
            {'data': {'is_exists_accounting': False},
             'results': [order_paid_not_exist,
                         order_not_paid_not_exist]},
            {'data': {'is_exists_accounting': True},
             'results': [order_paid_exist,
                         order_not_paid_exist]},
            {'data': {'is_paid': True},
             'results': [order_paid_exist,
                         order_paid_not_exist]},
            {'data': {'is_paid': False},
             'results': [order_not_paid_not_exist,
                         order_not_paid_exist]},
            {'data': {'is_exists_accounting': True, 'is_paid': True},
             'results': [order_paid_exist]},
            {'data': {'is_exists_accounting': True, 'is_paid': False},
             'results': [order_not_paid_exist]},
            {'data': {'is_exists_accounting': False, 'is_paid': False},
             'results': [order_not_paid_not_exist]},
        ]

        for elem in scenario:
            data = elem['data']
            expected_ids = [order.id for order in elem['results']]
            response = self.client.get(self.url_order_list, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            orders = response.context_data['orders']
            self.assertEqual(len(orders), len(expected_ids))
            for i, order_id in enumerate(expected_ids):
                self.assertEqual(order_id, orders[i].id)
