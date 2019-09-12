from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from oscar.test.factories import UserFactory

User = get_user_model()


class UserUpdateTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.admin = UserFactory(is_superuser=True, is_staff=True)

        cls.url_detail = reverse('dashboard:user-detail', args=(cls.user.id,))
        cls.url_create = reverse('dashboard:user-create')
        cls.url_list = reverse('dashboard:users-index')

    def test_permission(self):
        response = self.client.post(self.url_detail)
        expected_url = reverse('dashboard:login') + '?next={}'.format(self.url_detail)
        self.assertRedirects(response, expected_url)

    def test_update_errors(self):
        self.client.force_login(self.admin)

        response = self.client.post(self.url_detail)
        self.assertFormError(response, 'form', 'email', ['This field is required.'])

        data = {'email': self.admin.email}
        response = self.client.post(self.url_detail, data)
        self.assertFormError(response, 'form', 'email', ['User with this email already exists.'])

        data = {'email': self.user.email}
        response = self.client.post(self.url_detail, data)
        self.assertRedirects(response, self.url_detail)

    def test_update(self):
        self.client.force_login(self.admin)

        data = {
            'email': 'new@email.com',
            'first_name': 'Adam',
            'last_name': 'Smith',
            'phone_number': '+38099599999',
            'is_partner': True,
            'is_laboratory': False
        }
        response = self.client.post(self.url_detail, data)
        self.assertRedirects(response, self.url_detail)

        self.user.refresh_from_db()
        self.assertEqual(self.user.source, User.SOURCES.web)
        for field_name, value in data.items():
            self.assertEqual(getattr(self.user, field_name), value)

    def test_create_errors(self):
        self.client.force_login(self.admin)

        response = self.client.post(self.url_create)
        self.assertFormError(response, 'form', 'email', ['This field is required.'])

        data = {'email': self.admin.email}
        response = self.client.post(self.url_create, data)
        self.assertFormError(response, 'form', 'email', ['User with this email already exists.'])

        count_users = User.objects.count()

        data = {'email': 'new@email.com'}
        response = self.client.post(self.url_create, data)
        self.assertRedirects(response, self.url_list)
        self.assertEqual(User.objects.count(), count_users + 1)

    def test_create(self):
        self.client.force_login(self.admin)
        count_users = User.objects.count()

        data = {
            'email': 'new@email.com',
            'first_name': 'Adam',
            'last_name': 'Smith',
            'phone_number': '+38099599999',
            'is_partner': True,
            'is_laboratory': False
        }
        response = self.client.post(self.url_create, data)
        self.assertRedirects(response, self.url_list)
        self.assertEqual(User.objects.count(), count_users + 1)

        user = User.objects.get(email=data['email'])
        self.assertEqual(user.source, User.SOURCES.dashboard)

        for field_name, value in data.items():
            self.assertEqual(getattr(user, field_name), value)
