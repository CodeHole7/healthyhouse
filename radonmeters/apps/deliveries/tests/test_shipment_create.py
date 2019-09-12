from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from mock import patch
from oscar.test.factories import UserFactory, OrderFactory, OrderLineFactory, ProductFactory
from rest_framework import status

from deliveries.models import Shipment

User = get_user_model()


class TestCreateShipmentTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = UserFactory(is_staff=True, is_superuser=True)
        cls.product = ProductFactory(weight=10)
        cls.order = OrderFactory()
        OrderLineFactory(
            order=cls.order,
            product=cls.product,
        )

    def valid_create_shipment_response(data, title):
        return {'id': '7878'}

    @patch('deliveries.client._create_shipment', valid_create_shipment_response)
    def test_create_success(self):
        self.client.force_login(self.user)
        self.assertEqual(Shipment.objects.count(), 0)

        url = reverse('dashboard:shipment-create')
        data = {'order': self.order.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipment.objects.count(), 1)

    def test_create_no_order(self):
        self.client.force_login(self.user)
        self.assertEqual(Shipment.objects.count(), 0)

        url = reverse('dashboard:shipment-create')
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['errors'], {'order': ['This field is required.']})
        self.assertEqual(Shipment.objects.count(), 0)
