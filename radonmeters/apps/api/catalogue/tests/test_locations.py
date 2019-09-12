from oscar.core.loading import get_model
from oscar.test.factories.customer import UserFactory
from oscar.test.factories.order import OrderFactory
from oscar.test.factories.order import OrderLineFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from catalogue.models import Location
from catalogue.tests.factories import DosimeterFactory

Dosimeter = get_model('catalogue', 'Dosimeter')


class LocationAPITestCase(APITestCase):
    fixtures = ['locations']

    def setUp(self):
        super().setUp()

        self.admin = UserFactory(is_superuser=True, is_staff=True)

        self.url_list = reverse('api:locations:location-list')

    def test_permission(self):
        laboratory = UserFactory(is_laboratory=True)
        self.client.force_login(user=laboratory)
        response = self.client.post(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user1 = UserFactory()
        self.client.force_login(user=user1)
        response = self.client.post(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        self.client.force_login(user=self.admin)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 408)

        response_instance = response.data['results'][0]
        expected_data = {
            'id': 351,
            'name': '-'
        }
        self.assertEqual(response_instance, expected_data)

    def test_search(self):
        self.client.force_login(user=self.admin)
        data = {'q': 'stue'}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 72)

    def test_add_new(self):
        self.client.force_login(user=self.admin)
        data = {'name': 'new stue'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'q': 'stue'}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 73)

    def test_add_existing_value(self):
        self.client.force_login(user=self.admin)
        data = {'name': 'Havestue'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_delete(self):
        self.client.force_login(user=self.admin)

        obj = Location.objects.get(id=203)
        url = reverse('api:locations:location-detail', args=(obj.id, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data = {'q': 'stue'}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 71)
