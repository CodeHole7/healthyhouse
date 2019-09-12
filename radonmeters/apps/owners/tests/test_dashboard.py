from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from oscar.test.factories.customer import UserFactory


from owners.models import Owner
from owners.tests.factories import OwnerFactory


class OwnerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory(is_superuser=True, is_staff=True)
        cls.owner = OwnerFactory()

        cls.url_list = reverse('dashboard:owner-list')
        cls.url_add = reverse('dashboard:owner-create')
        cls.url_detail = reverse('dashboard:owner-detail', args=(cls.owner.id,))

    def test_permission(self):
        response = self.client.post(self.url_add)
        expected_url = reverse('dashboard:login') + \
                       '?next={}'.format(self.url_add)
        self.assertRedirects(response, expected_url)

    def test_empty_post(self):
        self.client.force_login(self.admin)

        response = self.client.post(self.url_add)
        errors = response.context_data['form'].errors
        self.assertTrue('first_name' in errors)
        self.assertTrue('last_name' in errors)
        self.assertTrue('is_default' in errors)

    def test_add_owner(self):
        self.client.force_login(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': True,
        }

        self.assertEqual(Owner.objects.count(), 1)

        response = self.client.post(self.url_add, data)
        self.assertRedirects(response, self.url_list)

        self.assertEqual(Owner.objects.count(), 2)

    def test_add_owner_no_one_default(self):
        self.client.force_login(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': False,
        }

        self.assertEqual(Owner.objects.count(), 1)

        response = self.client.post(self.url_add, data)
        self.assertTrue('is_default' in response.context_data['form'].errors)

    def test_add_owner_new_default(self):
        self.owner.is_default = True
        self.owner.save()

        self.client.force_login(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': True,
        }

        response = self.client.post(self.url_add, data)
        self.assertRedirects(response, self.url_list)

        old_owner = Owner.objects.get(id=self.owner.id)
        self.assertEqual(old_owner.is_default, False)

        new_owner = Owner.objects.get(email=data['email'])
        self.assertEqual(new_owner.is_default, True)

    def test_update_owner(self):
        self.client.force_login(self.admin)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email_owner@email.com',
            'is_default': True,
        }

        response = self.client.post(self.url_detail, data)
        self.assertRedirects(response, self.url_list)

        old_owner = Owner.objects.get(id=self.owner.id)
        self.assertEqual(old_owner.first_name, data['first_name'])
        self.assertEqual(old_owner.last_name, data['last_name'])
        self.assertEqual(old_owner.email, data['email'])

    def test_update_without_default(self):
        self.owner.is_default = True
        self.owner.save()

        self.client.force_login(self.admin)

        data = {
            'is_default': False,
        }

        response = self.client.post(self.url_detail, data)
        self.assertTrue('is_default' in response.context_data['form'].errors)

    def test_list(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context_data['owners']), 1)

    def test_list_filter(self):
        self.client.force_login(self.admin)

        data = {'email': 'email@em.com'}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context_data['owners']), 0)

        data = {'email': self.owner.email}
        response = self.client.get(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context_data['owners']), 1)
