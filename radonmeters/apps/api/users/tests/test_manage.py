from django.contrib.auth import get_user_model
from oscar.test.factories.customer import UserFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory(is_superuser=True, is_staff=True)
        cls.user = UserFactory()

        cls.url_list = reverse('api:users:user-list')
        cls.url_detail = reverse('api:users:user-detail', args=(cls.user.id,))

    def test_permission(self):
        response = self.client.post(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_post(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_add_user(self):
        self.client.force_authenticate(self.admin)

        user_count = User.objects.count()

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email@email.com',
        }

        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), user_count + 1)

    def test_update_user(self):
        self.client.force_authenticate(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'new_email@email.com',
            'phone_number': '+999999999',
        }

        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        for field_name, value in data.items():
            self.assertEqual(getattr(self.user, field_name), value)

    def test_list(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_filter(self):
        self.client.force_authenticate(self.admin)

        data = {'email': 'email@em.com'}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        data = {'email': self.user.email}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
