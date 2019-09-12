from oscar.test.factories.customer import UserFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from owners.models import Owner
from owners.tests.factories import OwnerFactory


class OwnerAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory(is_superuser=True, is_staff=True)
        cls.user = UserFactory()
        cls.owner = OwnerFactory()

        cls.url_list = reverse('api:owners:owner-list')
        cls.url_detail = reverse('api:owners:owner-detail', args=(cls.owner.id,))

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
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

    def test_add_owner(self):
        self.client.force_authenticate(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': True,
        }

        self.assertEqual(Owner.objects.count(), 1)

        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Owner.objects.count(), 2)

    def test_add_owner_no_one_default(self):
        self.client.force_authenticate(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': False,
        }

        self.assertEqual(Owner.objects.count(), 1)

        response = self.client.post(self.url_list, data)
        self.assertTrue('is_default' in response.data)

    def test_add_owner_new_default(self):
        self.owner.is_default = True
        self.owner.save()

        self.client.force_authenticate(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': True,
        }

        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_owner = Owner.objects.get(id=self.owner.id)
        self.assertEqual(old_owner.is_default, False)

        new_owner = Owner.objects.get(email=data['email'])
        self.assertEqual(new_owner.is_default, True)

    def test_update_owner(self):
        self.client.force_authenticate(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': True,
        }

        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        old_owner = Owner.objects.get(id=self.owner.id)
        self.assertEqual(old_owner.first_name, data['first_name'])
        self.assertEqual(old_owner.last_name, data['last_name'])
        self.assertEqual(old_owner.email, data['email'])

    def test_update_without_default(self):
        self.owner.is_default = True
        self.owner.save()

        self.client.force_authenticate(self.admin)

        data = {
            'is_default': False,
        }

        response = self.client.patch(self.url_detail, data)
        self.assertTrue('is_default' in response.data)

    def test_list(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_filter(self):
        self.client.force_authenticate(self.admin)

        data = {'email': 'email@em.com'}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        data = {'email': self.owner.email}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_search(self):
        self.client.force_authenticate(self.admin)
        o1 = OwnerFactory(first_name='first', last_name='last')
        o2 = OwnerFactory(first_name='second', last_name='last')
        o3 = OwnerFactory(first_name='new', last_name='new', email='second@email.com')

        scenario = [
            {'data': {'q': 'first'}, 'results': [o1]},
            {'data': {'q': 'second'}, 'results': [o2, o3]},
            {'data': {'q': 'new'}, 'results': [o3]},
            {'data': {'q': 'last'}, 'results': [o1, o2]},
        ]
        for data in scenario:
            search = data['data']
            # print('search', search)
            expected_results = data['results']
            response = self.client.get(self.url_list, search)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['count'], len(expected_results))
            results = response.data['results']
            for i, elem in enumerate(expected_results):
                self.assertEqual(elem.id, results[i]['id'])
