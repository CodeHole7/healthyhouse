from django.urls import reverse
from oscar.test.factories import UserFactory, PartnerFactory
from rest_framework import status
from rest_framework.test import APITestCase


class PartnerAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory(is_superuser=True, is_staff=True)

        PartnerFactory()

        cls.url_list = reverse('api:partners:partner-list')

    def test_permission(self):
        response = self.client.post(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
