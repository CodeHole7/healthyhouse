from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from oscar.test.factories import ProductFactory, UserFactory
from rest_framework import status

User = get_user_model()


class TestCheckoutSyncUserTestCase(TestCase):

    def test_checkout_anonymous(self):
        product = ProductFactory()
        # add product to basket
        url = reverse('basket:add', args=(product.id, ))
        data = {'quantity': 1}
        response = self.client.post(url, data, follow=True)
        expected_url = reverse('basket:summary')
        self.assertRedirects(response, expected_url)

        url_checkout = reverse('checkout:index')
        data = {'user_type': 'guest'}
        response = self.client.post(url_checkout, data, follow=True)
        # print(response.redirect_chain)
        url_shipping = reverse('checkout:shipping-address')
        self.assertRedirects(response, url_shipping)

        data = {
            'email': 'new@email.com',
            'phone_number': '+4520123456',
            'first_name': 'Adam',
            'last_name': 'Smith',
            'line1': 'Line1',
            'line4': 'Line4',
            'postcode': '90210',
            'country': 'da'
        }

        response = self.client.post(url_shipping, data, follow=True)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.phone_number, data['phone_number'])

    def test_checkout_auth_with_fields(self):
        user = UserFactory(first_name='John', last_name='Carter')
        self.client.force_login(user)

        product = ProductFactory()
        # add product to basket
        url = reverse('basket:add', args=(product.id, ))
        data = {'quantity': 1}
        response = self.client.post(url, data, follow=True)
        expected_url = reverse('basket:summary')
        self.assertRedirects(response, expected_url)

        url_checkout = reverse('checkout:index')
        data = {'user_type': 'guest'}
        response = self.client.post(url_checkout, data, follow=True)
        # print(response.redirect_chain)
        url_shipping = reverse('checkout:shipping-address')
        self.assertRedirects(response, url_shipping)

        data = {
            'email': 'new@email.com',
            'phone_number': '+4520123456',
            'first_name': 'Adam',
            'last_name': 'Smith',
            'line1': 'Line1',
            'line4': 'Line4',
            'postcode': '90210',
            'country': 'da'
        }

        response = self.client.post(url_shipping, data, follow=True)
        updated_user = User.objects.first()
        self.assertEqual(updated_user.email, user.email)
        self.assertNotEqual(updated_user.first_name, data['first_name'])
        self.assertNotEqual(updated_user.last_name, data['last_name'])
        self.assertNotEqual(updated_user.phone_number, data['phone_number'])

    def test_checkout_auth_without_fields(self):
        user = UserFactory(first_name='', last_name='')
        self.client.force_login(user)

        product = ProductFactory()
        # add product to basket
        url = reverse('basket:add', args=(product.id, ))
        data = {'quantity': 1}
        response = self.client.post(url, data, follow=True)
        expected_url = reverse('basket:summary')
        self.assertRedirects(response, expected_url)

        url_checkout = reverse('checkout:index')
        data = {'user_type': 'guest'}
        response = self.client.post(url_checkout, data, follow=True)
        # print(response.redirect_chain)
        url_shipping = reverse('checkout:shipping-address')
        self.assertRedirects(response, url_shipping)

        data = {
            'email': 'new@email.com',
            'phone_number': '+4520123456',
            'first_name': 'Adam',
            'last_name': 'Smith',
            'line1': 'Line1',
            'line4': 'Line4',
            'postcode': '90210',
            'country': 'da'
        }

        response = self.client.post(url_shipping, data, follow=True)
        updated_user = User.objects.first()
        self.assertEqual(updated_user.email, user.email)
        self.assertEqual(updated_user.first_name, data['first_name'])
        self.assertEqual(updated_user.last_name, data['last_name'])
        self.assertEqual(updated_user.phone_number, data['phone_number'])
