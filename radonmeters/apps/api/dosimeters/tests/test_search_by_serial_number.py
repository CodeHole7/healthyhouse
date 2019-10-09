from oscar.core.loading import get_model
from oscar.test.factories.customer import UserFactory
from oscar.test.factories.order import OrderFactory
from oscar.test.factories.order import OrderLineFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from catalogue.tests.factories import DosimeterFactory

Dosimeter = get_model('catalogue', 'Dosimeter')


class SeacrhDosimeterBySerialNumberAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()

        self.admin = UserFactory(is_superuser=True, is_staff=True)
        self.laboratory = UserFactory(is_laboratory=True)
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.dosimeter_1 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user1)))
        self.dosimeter_2 = DosimeterFactory(
            line=OrderLineFactory(order=OrderFactory(user=self.user2)))

        self.url = reverse('api:dosimeters:dosimeter-search-by-serial-number')

    def test_permission(self):
        self.client.force_login(user=self.laboratory)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_success(self):
        self.client.force_login(user=self.admin)
        data = {'serial_number': self.dosimeter_1.serial_number}
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'serial_number': self.dosimeter_1.serial_number,
            'dosimeter_id': self.dosimeter_1.id,
            'order_number':response.data['order_number']
        }
        self.assertDictEqual(response.data, expected_data)

    def test_search_failed(self):
        self.client.force_login(user=self.admin)
        data = {'serial_number': self.dosimeter_1.serial_number*2}
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_data = {
            'serial_number': ['Dosimeter was not found.']
        }
        self.assertDictEqual(response.data, expected_data)
