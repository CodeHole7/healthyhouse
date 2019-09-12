import random
from django.core import mail
from io import BytesIO
from mock import patch
from oscar.core.loading import get_model
from oscar.test.factories.catalogue import ProductFactory
from oscar.test.factories.customer import UserFactory
from oscar.test.factories.order import OrderFactory
from oscar.test.factories.order import OrderLineFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from config import settings
from order.signals import init_order_line_products

Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
ProductClass = get_model('catalogue', 'ProductClass')
DefaultProduct = get_model('catalogue', 'DefaultProduct')
Dosimeter = get_model('catalogue', 'Dosimeter')


class OrderGenerateLabelsTestCase(APITestCase):

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

        self.order = order = OrderFactory(user=UserFactory())
        OrderLineFactory(
            order=order,
            product=random.choice(self.dosimeters),
            quantity=random.randint(1, 2))

        # Generate objects for each item in the current order.
        # In real flow will be called when order will be placed.
        init_order_line_products(self, order=order)

        self.url_generate_labels = reverse('api:orders:order-generate-labels-pdf')
        self.url_send_labels = reverse('api:orders:order-send-labels-pdf')
        self.url_send_return_labels = reverse('api:orders:order-send-return-labels-pdf')
        self.url_generate_return_labels = reverse('api:orders:order-generate-return-labels-pdf')

    def test_action_permissions(self):
        response = self.client.post(self.url_generate_labels)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()
        response = self.client.get(self.url_generate_labels)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failed(self):
        response = self.client.get(self.url_generate_labels)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Labels can not be generated.')

    def test_failed_generation(self):
        self.order.shipping_id = '4545'
        self.order.save()

        o2 = OrderFactory(shipping_id='7878')

        with patch('api.order.views.OrderViewSet._generate_labels_pdf') as mock_label:
            mock_label.return_value = None, [self.order.number, o2.number]

            response = self.client.get(self.url_generate_labels)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data['detail'],
                f'Labels for order with number=[{self.order.number}, {o2.number}] can not be generated.')

    def test_success(self):
        self.order.shipping_id = '4545'
        self.order.save()

        with patch('api.order.views.OrderViewSet._generate_labels_pdf') as mock_label:
            thumb_io = BytesIO()
            mock_label.return_value = thumb_io.getvalue(), []

            response = self.client.get(self.url_generate_labels)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.get('Content-Disposition').startswith('attachment;'))

    def test_generate_return_labels(self):
        self.order.shipping_return_id = '4545'
        self.order.save()

        with patch('api.order.views.OrderViewSet._generate_labels_pdf') as mock_label:
            thumb_io = BytesIO()
            mock_label.return_value = thumb_io.getvalue(), []

            data = {'order_id': self.order.id}
            response = self.client.get(self.url_generate_return_labels, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.get('Content-Disposition').startswith('attachment;'))

    def test_send_return_labels(self):
        self.order.shipping_return_id = '4545'
        self.order.save()

        with patch('api.order.views.OrderViewSet._generate_labels_pdf') as mock_label:
            thumb_io = BytesIO()
            mock_label.return_value = thumb_io.getvalue(), []

            data = {'order_id': self.order.id}
            response = self.client.post(self.url_send_return_labels, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.to, [self.order.email])
            self.assertEqual(len(email.attachments), 1)

    def test_send_labels(self):
        self.order.shipping_id = '4545'
        self.order.save()

        with patch('api.order.views.OrderViewSet._generate_labels_pdf') as mock_label:
            thumb_io = BytesIO()
            mock_label.return_value = thumb_io.getvalue(), []

            data = {'order_id': self.order.id}
            response = self.client.post(self.url_send_labels, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.to, [self.order.email])
            self.assertEqual(len(email.attachments), 1)
