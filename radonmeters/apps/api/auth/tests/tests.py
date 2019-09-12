from oscar.test.factories.customer import UserFactory
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class AuthAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()

        # Create an user and auth token for him.
        self.password = 12345
        self.user = UserFactory(password=self.password)
        self.auth_token = Token.objects.create(user=self.user)

    def test_check_token(self):
        url = reverse('api:auth:check_token')

        # Make a request by non authenticated user.
        r = self.client.get(url)
        expected_data = {'detail': 'Authentication credentials were not provided.'}
        self.assertEqual(r.status_code, 401)
        self.assertDictEqual(r.data, expected_data)

        # Auth user.
        self.client.force_authenticate(self.user)

        # Make a request by authenticated user.
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.data, {})

    def test_login(self):
        url = reverse('api:auth:rest_login')
        data = {'email': self.user.email, 'password': self.password}

        # Make a request by non authenticated user.
        r = self.client.post(url, data, format='json')
        expected_data = {
            'key': self.auth_token.key,
            'is_staff': self.user.is_staff,
            'is_partner': self.user.is_partner,
            'is_laboratory': self.user.is_laboratory}
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.data, expected_data)

    def test_logout(self):
        url = reverse('api:auth:rest_logout')

        # Make a request by non authenticated user.
        r = self.client.post(url, {})
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.data, {'detail': 'Successfully logged out.'})

        # Make a request by authenticated user.
        self.client.force_authenticate(self.user)
        r = self.client.post(url)
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r.data, {'detail': 'Successfully logged out.'})
