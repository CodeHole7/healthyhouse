import json
from decimal import Decimal
from uuid import uuid4

import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
from oscar.core.loading import get_model
from oscar.test.factories.address import CountryFactory
from oscar.test.factories.catalogue import ProductClassFactory
from oscar.test.factories.catalogue import ProductFactory
from oscar.test.factories.customer import UserFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.data_import.tests.factories import DataImportDictFactory
from catalogue.tests.factories import DosimeterFactory
from data_import.models import ImportOrderObject
from owners.tests.factories import OwnerFactory

User = get_user_model()
Partner = get_model('partner', 'Partner')
Country = get_model('address', 'Country')
ShippingAddress = get_model('order', 'ShippingAddress')
BillingAddress = get_model('order', 'BillingAddress')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
Product = get_model('catalogue', 'Product')
Dosimeter = get_model('catalogue', 'Dosimeter')
DefaultProduct = get_model('catalogue', 'DefaultProduct')


def _decimal_format(value=0):
    return Decimal(value).quantize(Decimal('1.00'))


class ImportOrderAPITestCase(APITestCase):
    """
    Tests for DataImport API.
    """

    def setUp(self):
        super().setUp()

        self.maxDiff = 10000

        # Generate all needed instances.
        self.country = CountryFactory(
            iso_3166_1_a2='DK',
            printable_name='Denmark',
            is_shipping_country=True)
        self.product = ProductFactory(
            title=settings.OSCAR_PRODUCT_TYPE_DOSIMETER,
            product_class=ProductClassFactory(name=settings.OSCAR_PRODUCT_TYPE_DOSIMETER),
            slug='analog-closed-radon-measuring-box')
        self.user_email = 'user@example.com'
        self.user = UserFactory(email=self.user_email)
        self.partner = UserFactory(email='partner@example.com', is_partner=True)

        # Add partner auth token into each request.
        self.client.force_authenticate(self.partner)

    def test_admin_permission(self):
        admin = UserFactory(email=self.user_email, is_staff=True)
        self.client.force_authenticate(admin)
        url = reverse('api:data_import:orders')

        # Generate data for request.
        data = DataImportDictFactory(product=self.product.id)

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_import_valid_data(self):
        url = reverse('api:data_import:orders')

        # Generate data for request.
        data = DataImportDictFactory(product=self.product.id)

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # Get all created instances from database.
        billing_address = BillingAddress.objects.last()
        dosimeters = Dosimeter.objects.all().order_by('created')[:data['quantity']]
        line = Line.objects.last()
        order = Order.objects.last()
        shipping_address = ShippingAddress.objects.last()
        user = get_user_model().objects.get(email=data['email'])

        # Prepare expected data of main response.
        expected_data = {
            'billing_address_id': billing_address.pk,
            'dosimeters': [str(d.id) for d in dosimeters],
            'line_id': line.pk,
            'order_id': order.pk,
            'shipping_address_id': shipping_address.pk,
            'user_id': user.pk}

        # Check body of response.
        self.assertJSONEqual(json.dumps(r.data), expected_data)

        # =====================================================================
        # CHECK CREATED INSTANCES.
        # =====================================================================

        # Checks for instance of User.
        # ---------------------------------------------------------------------
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.phone_number, data['phone_number'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.source, User.SOURCES.imported)

        # Checks for instance of BillingAddress.
        # ---------------------------------------------------------------------
        self.assertEqual(billing_address.first_name, data['first_name'])
        self.assertEqual(billing_address.last_name, data['last_name'])
        self.assertEqual(billing_address.line1, data['line1'])
        self.assertEqual(billing_address.state, data['state'])
        self.assertEqual(billing_address.postcode, data['postcode'])
        self.assertEqual(billing_address.country.iso_3166_1_a2, data['country'])

        # Checks for instance of ShippingAddress.
        # ---------------------------------------------------------------------
        self.assertEqual(shipping_address.first_name, data['first_name'])
        self.assertEqual(shipping_address.last_name, data['last_name'])
        self.assertEqual(shipping_address.line1, data['line1'])
        self.assertEqual(shipping_address.state, data['state'])
        self.assertEqual(shipping_address.postcode, data['postcode'])
        self.assertEqual(shipping_address.country.iso_3166_1_a2, data['country'])
        self.assertEqual(shipping_address.phone_number, data['phone_number'])

        # Checks for instance of Order.
        # ---------------------------------------------------------------------
        self.assertEqual(order.site, Site.objects.get_current())
        self.assertEqual(order.user, user)
        self.assertEqual(order.billing_address, billing_address)
        self.assertEqual(order.shipping_address, shipping_address)
        self.assertEqual(order.currency, data['currency'])
        self.assertEqual(order.shipping_method, data['shipping_method'])
        self.assertEqual(order.shipping_code, data['shipping_code'])
        # self.assertEqual(order.shipping_id, data['shipping_id'])
        self.assertEqual(order.status, data['status'])
        self.assertEqual(order.date_placed.strftime('%d-%m-%Y %H:%m'), data['date_placed'])
        self.assertEqual(order.total_incl_tax, _decimal_format(data['total_incl_tax']))
        self.assertEqual(order.total_excl_tax, _decimal_format(data['total_excl_tax']))
        self.assertEqual(order.shipping_incl_tax, _decimal_format(data['shipping_incl_tax']))
        self.assertEqual(order.shipping_excl_tax, _decimal_format(data['shipping_excl_tax']))

        # Checks for instance of Line.
        # ---------------------------------------------------------------------
        self.assertEqual(line.order, order)
        self.assertEqual(line.product.pk, data['product'])
        self.assertEqual(line.quantity, data['quantity'])
        self.assertEqual(line.line_price_incl_tax, _decimal_format(data['total_incl_tax']))
        self.assertEqual(line.line_price_excl_tax, _decimal_format(data['total_excl_tax']))
        self.assertEqual(line.line_price_before_discounts_incl_tax, _decimal_format(data['total_incl_tax']))
        self.assertEqual(line.line_price_before_discounts_excl_tax, _decimal_format(data['total_excl_tax']))

        # Checks for instances of Dosimeter.
        # ---------------------------------------------------------------------
        self.assertEqual(dosimeters.count(), data['quantity'])
        for idx, d in enumerate(dosimeters):
            self.assertEqual(d.line, line)
            self.assertEqual(d.serial_number, data['serial_numbers'][idx])

        # Checks for instance of ImportOrderObject.
        # ---------------------------------------------------------------------
        import_order_obj = ImportOrderObject.objects.first()
        self.assertJSONEqual(import_order_obj.raw_data, json.dumps(data))

        # Make a duplicated request.
        # =====================================================================
        data['serial_numbers'] = [str(uuid4()) for _ in range(data['quantity'])]
        # with email which should be stripped
        data['email'] = '\tsba@km.dk'
        r = self.client.post(url, data, type='json')

        # Check the status code of response is again 201.
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        new_user = get_user_model().objects.last()
        self.assertNotEqual(new_user.email, data['email'])
        self.assertEqual(new_user.email, data['email'].strip())

    def test_import_with_owner(self):
        url = reverse('api:data_import:orders')

        # Generate data for request.
        data = DataImportDictFactory(product=self.product.id)
        owner = OwnerFactory()
        data['owner'] = owner.id

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # Get all created instances from database.
        order = Order.objects.last()

        # Check owner in order.
        # ---------------------------------------------------------------------
        self.assertEqual(order.owner, owner)

    def test_import_invalid_serial_numbers(self):
        url = reverse('api:data_import:orders')

        # Serial numbers are not unique.
        # =====================================================================
        data = DataImportDictFactory(product=self.product.id)
        data['quantity'] = 6
        data['serial_numbers'] = [1, 1, 2, 3, 3, 4]

        # Prepare expected data.
        expected_data = {'serial_numbers': ['Serial numbers must be unique.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

        # Serial numbers already exists in database.
        # =====================================================================
        serial_number = uuid4().hex
        DosimeterFactory(serial_number=serial_number)

        data = DataImportDictFactory(
            quantity=1,
            product=self.product.pk,
            serial_numbers=[serial_number])

        # Prepare expected data.
        err = 'Next serial numbers already exists in the database: %s.' % serial_number
        expected_data = {'serial_numbers': [err]}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

        # Number of serial numbers is not the same as quantity.
        # =====================================================================
        data = DataImportDictFactory(product=self.product.id)
        data['quantity'] = 3
        data['serial_numbers'] = [1, 2] # too few serial numbers
        # Prepare expected data.
        expected_data = {'serial_numbers': ['Number of serial numbers must be the same as quantity.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

        # Check when too many serial numbers are given
        data['serial_numbers'] = [1, 2, 3, 4]
        r = self.client.post(url, data, type='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)
    
    def test_import_created_order(self):
        """Test that order with status 'created' cannot be imported with serial numbers.
        """
        url = reverse('api:data_import:orders')

        data = DataImportDictFactory(product=self.product.id)
        data['status'] = 'created'

        # Prepare expected data.
        expected_data = {'serial_numbers': ['When importing orders with status "created", serial numbers should not be provided.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

        del data['serial_numbers']
        r = self.client.post(url, data, type='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)


    def test_import_required_quantity(self):
        url = reverse('api:data_import:orders')

        data = DataImportDictFactory(product=self.product.id)
        del data['quantity']

        # Prepare expected data.
        expected_data = {'quantity': ['This field is required.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

    def test_import_positive_quantity(self):
        url = reverse('api:data_import:orders')

        data = DataImportDictFactory(product=self.product.id)
        data['quantity'] = 0

        # Prepare expected data.
        expected_data = {'quantity': ['Ensure this value is greater than or equal to 1.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

        # Try negative quantity also.
        data['quantity'] = -1
        r = self.client.post(url, data, type='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

    
    def test_import_required_owner(self):
        url = reverse('api:data_import:orders')

        data = DataImportDictFactory(product=self.product.id)
        del data['owner']

        # Prepare expected data.
        expected_data = {'owner': ['This field is required.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

    def test_import_serial_numbers_string(self):
        url = reverse('api:data_import:orders')

        data = DataImportDictFactory(product=self.product.id)
        # data['serial_numbers'] = '[1, 3]'
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_import_invalid_partner(self):
        url = reverse('api:data_import:orders')

        # Invalid partner_code
        # =====================================================================
        data = DataImportDictFactory(partner_code='invalid', product=self.product.id)

        # Prepare expected data.
        expected_data = {'partner_code': ['Partner was not found.']}

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(r.data, expected_data)

        # Empty partner
        data = {'partner_code': ''}
        r = self.client.post(url, data, type='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('partner_code' not in r.data)

    def test_import_invalid_calculated_values(self):
        url = reverse('api:data_import:orders')

        data = DataImportDictFactory(
            product=self.product.id,
            total_excl_tax=None,
            shipping_excl_tax=None,
            partner_code=''
        )

        # Make a request.
        r = self.client.post(url, data, type='json')

        # Check the status code of response.
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        order = Order.objects.last()
        line = order.lines.first()
        self.assertEqual(line.partner, None)
        self.assertEqual(line.partner_name, '')
        self.assertEqual(line.partner_sku, '')


class ImportAppAPITestCase(APITestCase):
    """
    Tests for testing Import of applications via API.
    """

    def test_import_app(self):
        self.su = UserFactory(email='super@user.com', is_superuser=True)
        self.client.force_authenticate(self.su)

        # Generate filename.
        name = 'Name with Spaces,Symbols AND uuid code [%s].ipa' % uuid4().hex

        # Generate data for request.
        attachment = SimpleUploadedFile(
            name=name,
            content=b'file_content',
            content_type='application/octet-stream')

        # Prepare data for request.
        data = {'os': 'ios', 'app': attachment}

        # Prepare expected data.
        name, ext = os.path.splitext(name)
        filename = slugify(name) + ext
        expected_data = {
            'detail': 'Application was successfully uploaded.',
            'url': settings.MEDIA_URL + 'downloads/apps/ios/' + filename}

        # Make a request.
        url = reverse('api:data_import:apps')
        r = self.client.post(url, data, format='multipart')

        # Check that file was successfully result.
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.data, expected_data)

        # Generate path to uploaded file:
        path = 'downloads/apps/{os}/{filename}'.format(
            os=data['os'],
            filename=filename)

        # Remove uploaded file.
        os.remove(os.path.join(settings.MEDIA_ROOT, settings.MEDIA_ROOT, path))

        # Check that uploaded file was removed.
        self.assertRaises(
            FileNotFoundError,
            os.remove,
            os.path.join(settings.MEDIA_ROOT, settings.MEDIA_ROOT, path))
