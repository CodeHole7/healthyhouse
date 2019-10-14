from io import BytesIO
import json
from datetime import timedelta
from django.utils.http import urlencode

import random
from django.core import mail
from django.db.models import Count
from django.utils import timezone

from oscar.core.loading import get_model
from oscar.test.factories.catalogue import ProductFactory
from oscar.test.factories.customer import UserFactory
from oscar.test.factories.order import OrderFactory
from oscar.test.factories.order import OrderLineFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from catalogue.tests.factories import DosimeterFactory
from common.utils import custom_format_currency
from config import settings
from order.signals import init_order_line_products
from owners.tests.factories import OwnerFactory, OwnerEmailConfigFactory

Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
ProductClass = get_model('catalogue', 'ProductClass')
DefaultProduct = get_model('catalogue', 'DefaultProduct')
Dosimeter = get_model('catalogue', 'Dosimeter')


def serialize_line_items(line):
    """
    :return: [
        {
            "id": "uuid4",
            "serial_number": "string"
        },
        ...
    ]
    """
    if line.products.exists():
        return [
            {
                'id': str(p['id']),
                'serial_number': p['serial_number'],
                'item_type': 'default_product',
            }
            for p in line.products.values('id', 'serial_number')]
    elif line.dosimeters.exists():
        return [
            {
                'id': str(d['id']),
                'serial_number': d['serial_number'],
                'item_type': 'dosimeter',
            }
            for d in line.dosimeters.values('id', 'serial_number')]
    else:
        return []


def serialize_lines(lines):
    """
    :return: [
        {
            "id": 3722,
            "title": "",
            "upc": None,
            "quantity": 1,
            "items": [
                {
                    "uuid": "string",
                },
                ...
            ]
        },
        ...
    ]
    """
    data = []

    for line in lines:
        data.append(
            {
                "id": line.id,
                "title": line.title,
                "upc": line.upc,
                "quantity": line.quantity,
                "items": serialize_line_items(line),
                'product_id':line.product_id
            }
        )
    return data


def serialize_order(order):
    return {
        'id': order.id,
        'lines': serialize_lines(order.lines.all()),
        'number': order.number,
        'quantity': order.num_items,
        "billing_address": {
            "title": order.billing_address.title,
            "first_name": order.billing_address.first_name,
            "last_name": order.billing_address.last_name,
            "line1": order.billing_address.line1,
            "line2": order.billing_address.line2,
            "line3": order.billing_address.line3,
            "line4": order.billing_address.line4,
            "state": order.billing_address.state,
            "postcode": order.billing_address.postcode,
            "country": order.billing_address.country.code,
        },
        "shipping_address": {
            "title": order.shipping_address.title,
            "first_name": order.shipping_address.first_name,
            "last_name": order.shipping_address.last_name,
            "line1": order.shipping_address.line1,
            "line2": order.shipping_address.line2,
            "line3": order.shipping_address.line3,
            "line4": order.shipping_address.line4,
            "state": order.shipping_address.state,
            "postcode": order.shipping_address.postcode,
            "country": order.shipping_address.country.code,
            "phone_number": order.shipping_address.phone_number,
        },
        'status': order.status,
        'currency': order.currency,
        'shipping_incl_tax': str(order.shipping_incl_tax),
        'shipping_method': order.shipping_method,
        'shipping_code': order.shipping_id,
        'shipping_id': order.shipping_id,
        'date_placed': order.date_placed.strftime(settings.DATE_FORMAT_REST),
        'is_reported_by_partner': order.is_reported_by_partner,
        'is_report_sent': order.is_report_sent,
        'sent_date': order.sent_date,
        'is_approved': order.is_approved,
        'approved_date': order.approved_date,
        'user_who_approved': order.user_who_approved_id,
        
        'email': order.user.email,
        'phone_number': order.user.phone_number,
        'total_price': custom_format_currency(
            number=order.total_incl_tax,
            currency=order.currency
        ),
        'total_excl_tax': str(order.total_excl_tax),
        'total_incl_tax': str(order.total_incl_tax),
        'is_exists_accounting': order.is_exists_accounting,
        'is_paid': order.is_paid,
        'date_payment': order.date_payment,
    }


def serialize_orders(orders, page_size=settings.REST_FRAMEWORK['PAGE_SIZE']):
    return sorted(
        [{
            'id': order.id,
            'number': order.number,
            'quantity': order.num_items,
            'status': order.status,
            'shipping_code': order.shipping_code,
            'shipping_id': order.shipping_id,
            'date_placed': order.date_placed.strftime(settings.DATE_FORMAT_REST),
            'owner': order.owner_id,
            'is_reported_by_partner': order.is_reported_by_partner,
            'is_report_sent': order.is_report_sent,
            'sent_date': order.sent_date,
            'is_approved': order.is_approved,
            'approved_date': order.approved_date,
            'user_who_approved': order.user_who_approved_id,
            'is_exists_accounting': order.is_exists_accounting,
            'is_paid': order.is_paid,
            'date_payment': order.date_payment,
        } for order in orders],
        key=lambda o: o['date_placed'],
        reverse=True
    )[:page_size]


class OrderAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()

        self.maxDiff = 10000

        # Create and authenticate him in system.
        self.admin = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_authenticate(self.admin)

        # Create product classes.
        self.pc_default = ProductClass.objects.create(
            name=settings.OSCAR_PRODUCT_TYPE_DEFAULT)
        self.pc_dosimeter = ProductClass.objects.create(
            name=settings.OSCAR_PRODUCT_TYPE_DOSIMETER)

        # Create default products.
        self.products = [
            ProductFactory(
                product_class=self.pc_default,
                title='Product #%s' % i
            ) for i in range(1, 10)
        ]

        # Create dosimeters.
        self.dosimeters = [
            ProductFactory(
                product_class=self.pc_dosimeter,
                title='Dosimeter #%s' % i
            ) for i in range(1, 10)
        ]

        # Prepare orders.
        OrderFactory.create_batch(20, user=UserFactory())
        self.orders = Order.objects.all()
        for order in self.orders:
            OrderLineFactory(
                order=order,
                product=random.choice(self.products),
                quantity=random.randint(1, 2))
            OrderLineFactory(
                order=order,
                product=random.choice(self.dosimeters),
                quantity=random.randint(1, 2))

            # Generate objects for each item in the current order.
            # In real flow will be called when order will be placed.
            init_order_line_products(self, order=order)

            # Set random status for current order.
            order.set_status(random.choice(order.available_statuses()))

    def test_action_premissions(self):
        url = reverse('api:orders:order-list')

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_order_list(self):
        url = reverse('api:orders:order-list')

        # Make a request without filtering by status:
        r = self.client.get(url)
        expected_data = serialize_orders(self.orders)
        self.assertEqual(r.data['count'], self.orders.count())
        dosimeters_count = self.orders.aggregate(dc=Count('lines__dosimeters'))['dc']
        self.assertEqual(r.data['dosimeters_count'], dosimeters_count)
        self.assertJSONEqual(json.dumps(r.data['results']), expected_data)

        # Make the requests with filtering by status:
        for status in settings.OSCAR_ORDER_STATUS_PIPELINE.keys():
            filtered_orders = Order.objects.filter(status=status)
            r = self.client.get(url, {'status': status})
            expected_data = serialize_orders(filtered_orders)
            self.assertEqual(r.data['count'], filtered_orders.count())
            self.assertJSONEqual(json.dumps(r.data['results']), expected_data)

        # Make the requests with filtering by order's number:
        order = Order.objects.first()
        order_number = order.number[-1]  # needed for check `icontains`.
        filtered_orders = Order.objects.filter(number__icontains=order_number)
        r = self.client.get(url, {'q': order_number})
        expected_data = serialize_orders(filtered_orders)
        self.assertEqual(r.data['count'], filtered_orders.count())
        self.assertJSONEqual(json.dumps(r.data['results']), expected_data)

    def test_get_order_details(self):
        order = Order.objects.last()
        url = reverse('api:orders:order-detail', kwargs={'pk': order.pk})
        r = self.client.get(url)
        expected_data = serialize_order(order)
        print('\n\n\n\n\n\n\n\n\n')
        print(json.dumps(r.data))
        print('\n\n\n\n\n\n\n\n\n')
        print(expected_data)
        self.assertJSONEqual(json.dumps(r.data), expected_data)

    def test_change_order_status(self):

        # Prepare order with one default product and one dosimeter.
        order = OrderFactory(status='created')

        # Generate lines with different default products.
        OrderLineFactory(
            order=order,
            product=self.products[0],
            quantity=3)
        OrderLineFactory(
            order=order,
            product=self.products[1],
            quantity=1)

        # Generate lines with different dosimeters.
        OrderLineFactory(
            order=order,
            product=self.dosimeters[0],
            quantity=3)
        OrderLineFactory(
            order=order,
            product=self.dosimeters[1],
            quantity=1)

        # Generate objects for each item in the current order.
        # In real flow will be called when order will be placed.
        init_order_line_products(self, order=order)

        # Change status when it's impossible (not all serial numbers have been set):
        url = reverse('api:orders:order-change-status', kwargs={'pk': order.pk})
        r = self.client.patch(url)
        order.refresh_from_db()
        expected_data = {
            'detail': 'Status cannot be changed to "issued". '
                      'Might not all product items have a serial number.'}
        self.assertJSONEqual(json.dumps(r.data), expected_data)

        # Add serial numbers for all items in the order.
        DefaultProduct.objects.filter(line__in=order.lines.all()).update(serial_number=1)
        Dosimeter.objects.filter(line__in=order.lines.all()).update(serial_number=1)

        # Change status when it's possible (all serial numbers have been set):
        url = reverse('api:orders:order-change-status', kwargs={'pk': order.pk})
        r = self.client.patch(url)
        order.refresh_from_db()
        expected_data = {'detail': 'Status has been changed to "issued".'}
        self.assertJSONEqual(json.dumps(r.data), expected_data)

    def test_set_serial_number_for_dosimeter(self):
        # Get object for generate an URL and send request.
        order = self.orders.first()
        obj = Dosimeter.objects.filter(line__in=order.lines.all()).first()
        url = reverse('api:orders:dosimeter-detail', kwargs={'pk': obj.pk})

        # Send request with blank `serial_number`.
        # ---------------------------------------------------------------------
        r = self.client.patch(url, {}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(json.dumps(r.data), {'serial_number': ''})

        # Send request with value in `serial_number`.
        # ---------------------------------------------------------------------
        self.assertEqual(obj.serial_number, '')
        r = self.client.patch(url, {'serial_number': 123}, format='json')
        obj.refresh_from_db()
        self.assertEqual(obj.serial_number, '123')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(json.dumps(r.data), {'serial_number': '123'})

    def test_set_serial_number_for_default_product(self):
        # Get object for generate an URL and send request.
        order = self.orders.first()
        obj = DefaultProduct.objects.filter(line__in=order.lines.all()).first()
        url = reverse('api:orders:default-product-detail', kwargs={'pk': obj.pk})

        # Send request with blank `serial_number`.
        # ---------------------------------------------------------------------
        r = self.client.patch(url, {}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(json.dumps(r.data), {'serial_number': ''})

        # Send request with value in `serial_number`.
        # ---------------------------------------------------------------------
        self.assertEqual(obj.serial_number, '')
        r = self.client.patch(url, {'serial_number': 123}, format='json')
        obj.refresh_from_db()
        self.assertEqual(obj.serial_number, '123')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(json.dumps(r.data), {'serial_number': '123'})

    def test_owner_to_order(self):
        owner = OwnerFactory()

        order = self.orders.first()
        url = reverse('api:orders:order-detail', args=(order.id, ))

        data = {
            'owner': owner.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.owner_id, owner.id)

    def test_update_payment_data(self):
        order = self.orders.first()
        url = reverse('api:orders:order-detail', args=(order.id, ))

        self.assertEqual(order.is_exists_accounting, False)
        self.assertEqual(order.is_paid, False)
        self.assertEqual(order.date_payment, None)

        data = {
            'is_exists_accounting': True,
            'is_paid': True,
            'date_payment': timezone.now().strftime('%d-%m-%Y')
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.is_exists_accounting, False)
        self.assertEqual(order.is_paid, True)
        self.assertEqual(order.date_payment.date(), timezone.now().date())

        response = self.client.get(url)
        result = response.json()
        self.assertEqual(result['date_payment'], data['date_payment'])


class OrderPredictableAPITestCase(APITestCase):
    fixtures = ['product_classes', 'products']

    def setUp(self):
        super().setUp()

        self.maxDiff = None

        self.admin = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_authenticate(self.admin)

        user1 = UserFactory()
        self.order = OrderFactory(user=user1)
        line = OrderLineFactory(order=self.order)
        date_start = timezone.now()
        date_end = date_start + timedelta(days=2)

        self.d_1 = DosimeterFactory(
            line=line,
            active_area=False, floor=-1, location='corner',
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=120,
            uncertainty=30)

        self.d_2 = DosimeterFactory(
            line=line,
            active_area=False, floor=0, location='table',
            measurement_start_date=date_start,
            measurement_end_date=date_end,
            concentration=30,
            uncertainty=40)

        self.url_approve = reverse('api:orders:order-approve', args=(self.order.id, ))
        self.url_send_report = reverse('api:orders:order-send-report', args=(self.order.id,))
        self.url_detail = reverse('api:orders:order-detail', args=(self.order.id,))
        
        self.url_change_use_external_report = reverse('api:orders:order-change-use-external-report', args=(self.order.id,))
        self.url_upload_external_report = reverse('api:orders:order-upload-external-report', args=(self.order.id,))

    def test_no_approve(self):
        """Check that non-full or weird order cannot be approved.
        """
        order = self.order
        self.d_2.uncertainty = None # non-full
        self.d_2.save()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        response = self.client.post(self.url_approve, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['forceApprove'], False)

        order.refresh_from_db()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        self.d_2.uncertainty = 30
        self.d_2.location = '' # non-full
        self.d_2.save()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        response = self.client.post(self.url_approve, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['forceApprove'], False)

        order.refresh_from_db()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        self.d_2.location = 'table'
        self.d_2.floor = None # non-full
        self.d_2.save()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        response = self.client.post(self.url_approve, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['forceApprove'], False)

        order.refresh_from_db()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        self.d_2.floor = 0
        self.d_2.concentration = 1000 # weird
        self.d_2.save()
        self.order.update_weirdness_statuses()
        self.order.save()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        response = self.client.post(self.url_approve, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['forceApprove'], True)

        order.refresh_from_db()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

    def test_approve_no_report(self):
        order = self.order
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)

        now = timezone.now()

        response = self.client.post(self.url_approve, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_who_approved'], self.admin.email)
        self.assertEqual(response.data['approved_date'], now.date().strftime(settings.DATE_FORMAT_REST))

        # no report
        self.assertEqual(len(mail.outbox), 0)

        order.refresh_from_db()
        self.assertEqual(order.is_approved, True)
        self.assertEqual(order.approved_date.date(), now.date())
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, self.admin)

    def test_approve_force_weird(self):
        """Test approval procedure for weird orders.
        """
        order = self.order

        self.d_2.concentration = 1000 # weird
        self.d_2.save()
        self.order.update_weirdness_statuses()
        self.order.save()
        self.assertEqual(order.is_approved, False)
        self.assertEqual(order.approved_date, None)
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, None)
        self.assertEqual(order.not_weird, False)

        now = timezone.now()

        explanation = 'The order is fine, though it is looking weird'
        response = self.client.post(self.url_approve, urlencode({'not_weird_override': 'true', 'not_weird_explanation': explanation}), content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_who_approved'], self.admin.email)
        self.assertEqual(response.data['approved_date'], now.date().strftime(settings.DATE_FORMAT_REST))

        # no report
        self.assertEqual(len(mail.outbox), 0)

        order.refresh_from_db()
        self.assertEqual(order.is_approved, True)
        self.assertEqual(order.approved_date.date(), now.date())
        self.assertEqual(order.is_report_sent, False)
        self.assertEqual(order.user_who_approved, self.admin)
        self.assertEqual(order.not_weird, True)
        self.assertEqual(order.not_weird_explanation, explanation)

    def test_send_report_no_approve(self):
        response = self.client.post(self.url_send_report, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['details'], 'You need to approve report firstly.')

    def test_send_report_approved(self):
        order = self.order
        order.is_approved = True
        order.save()
        self.assertEqual(order.is_report_sent, False)

        response = self.client.post(self.url_send_report, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # report to customer
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [order.user.email])

        order.refresh_from_db()
        self.assertEqual(order.is_report_sent, True)

    def test_send_report_owner_from(self):
        order = self.order
        order.is_approved = True

        # owner has email
        owner_config = OwnerEmailConfigFactory(from_email='owner@email.com')
        order.owner = owner = owner_config.owner
        order.save()
        self.assertEqual(order.is_report_sent, False)

        response = self.client.post(self.url_send_report, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [order.user.email])
        self.assertEqual(mail.outbox[0].from_email, owner_config.from_email)

        # owner email is empty
        owner_config.from_email = ''
        owner_config.save()

        response = self.client.post(self.url_send_report, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, [order.user.email])
        self.assertEqual(mail.outbox[1].from_email, settings.DEFAULT_FROM_EMAIL)

        # order without owner
        order.owner = None
        order.save()

        response = self.client.post(self.url_send_report, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[2].to, [order.user.email])
        self.assertEqual(mail.outbox[2].from_email, settings.DEFAULT_FROM_EMAIL)

    # def test_send_report_reported_by_partner(self):
    #     order = self.order
    #     order.is_approved = True
    #     order.is_reported_by_partner = True
    #     order.save()
    #     self.assertEqual(order.is_report_sent, False)
    #
    #     response = self.client.post(self.url_send_report, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['details'], 'This order was reported by partner.')
    #
    #     order.refresh_from_db()
    #     self.assertEqual(order.is_report_sent, False)

    def test_order_patch(self):
        order = self.order
        self.assertEqual(order.is_reported_by_partner, False)

        data = {
            'is_reported_by_partner': True,
            'is_report_sent': True
        }

        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.is_reported_by_partner, True)
        self.assertEqual(order.is_report_sent, False)

    def test_external_report(self):
        order = self.order
        order.use_external_report = False
        order.external_report_pdf.delete()
        order.save()

        # Should be not possible to use external report when no file is uploaded
        response = self.client.post(self.url_change_use_external_report, urlencode({'use_external_report': 'checked'}), content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertEqual(order.use_external_report, False)

        # Should be possible to upload an external report
        pdf_file = BytesIO(b'%PDF-...') # not a valid pdf, but first 4 bytes are correct at least
        pdf_file.name = 'report.pdf'
        response = self.client.post(self.url_upload_external_report, {'external_report_pdf': pdf_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertTrue(order.external_report_pdf)
        self.assertEqual(order.use_external_report, True)

        # Now should be possible to check and un-checx use_external_report
        response = self.client.post(self.url_change_use_external_report, urlencode({}), content_type="application/x-www-form-urlencoded")
        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.use_external_report, False)

        response = self.client.post(self.url_change_use_external_report, urlencode({'use_external_report': 'checked'}), content_type="application/x-www-form-urlencoded")
        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.use_external_report, True)
