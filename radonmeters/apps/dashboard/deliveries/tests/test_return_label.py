import json

from django.core.exceptions import ValidationError
from mock import patch
from oscar.test.factories.order import OrderFactory

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from oscar.core.loading import get_model
from oscar.test.factories import UserFactory
from rest_framework import status

User = get_user_model()
ShipmentReturn = get_model('deliveries', 'ShipmentReturn')
Shipment = get_model('deliveries', 'Shipment')
Order = get_model('order', 'Order')


class UserUpdateTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.admin = UserFactory(is_superuser=True, is_staff=True)
        cls.url_create = reverse('dashboard:shipment-return-create')

    def setUp(self):
        super().setUp()
        self.order = OrderFactory(user=self.user)

    def test_permission(self):
        response = self.client.post(self.url_create)
        expected_url = reverse('dashboard:login') + '?next={}'.format(self.url_create)
        self.assertRedirects(response, expected_url)

    def test_create_invalid(self):
        self.client.force_login(self.admin)

        self.assertEqual(hasattr(self.order, 'shipment_return'), False)

        data = {
            'order': self.order.id,
        }
        response = self.client.post(self.url_create, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(self.url_create, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('order', response.json()['errors'])

    def valid_create_shipment_response(data, title):
        return {'id': '7878'}

    @patch('deliveries.client._create_shipment', valid_create_shipment_response)
    def test_create(self):
        self.client.force_login(self.admin)

        self.assertEqual(hasattr(self.order, 'shipment_return'), False)

        data = {
            'order': self.order.id,
        }

        response = self.client.post(
            self.url_create, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_return_id, '7878')

        self.assertEqual(ShipmentReturn.objects.count(), 1)
        shipment_return = ShipmentReturn.objects.first()
        self.assertEqual(shipment_return.order, self.order)
        self.assertEqual(shipment_return.data['id'], self.order.shipping_return_id)

        order = Order.objects.get(id=self.order.id)
        self.assertEqual(hasattr(order, 'shipment_return'), True)

    def empty_shipment_response(data, title):
        raise ValidationError('Invalid request. {}')

    @patch('deliveries.client._create_shipment', empty_shipment_response)
    def test_create_invalid(self):
        self.client.force_login(self.admin)

        self.assertEqual(hasattr(self.order, 'shipment_return'), False)

        data = {
            'order': self.order.id,
        }

        response = self.client.post(
            self.url_create, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_return_id, '')
        self.assertEqual(ShipmentReturn.objects.count(), 0)

    def test_change_return_shipment(self):
        self.client.force_login(self.admin)

        shipment_return = ShipmentReturn.objects.create(
            order=self.order,
            data={'id': '123'}
        )
        self.order.shipping_return_id = '123'
        self.order.save()

        new_id = '123123'
        data = {
            'order': self.order.id,
            'data': json.dumps({'id': new_id})
        }

        url = reverse('dashboard:shipment-return-update', args=[shipment_return.id])

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_return_id, new_id)

        shipment_return.refresh_from_db()
        self.assertEqual(shipment_return.data['id'], new_id)

    def test_change_shipment(self):
        self.client.force_login(self.admin)

        shipment = Shipment.objects.create(
            order=self.order,
            data={'id': '123'}
        )
        self.order.shipping_id = '123'
        self.order.save()

        new_id = '123123'
        data = {
            'order': self.order.id,
            'data': json.dumps({'id': new_id})
        }

        url = reverse('dashboard:shipment-update', args=[shipment.id])

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_id, new_id)

        shipment.refresh_from_db()
        self.assertEqual(shipment.data['id'], new_id)
