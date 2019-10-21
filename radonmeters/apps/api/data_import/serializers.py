import json
from uuid import uuid4

import os
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.core import exceptions as django_exceptions
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from model_utils import Choices
from oscar.apps.checkout.forms import ShippingAddressForm
from oscar.apps.order.utils import OrderNumberGenerator
from oscar.apps.payment.forms import BillingAddressForm
from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.order.serializers import OrderAccountingLedgerSerializer

from deliveries.client import get_shipment_request
from deliveries.models import Shipment
from owners.models import Owner

User = get_user_model()
Basket = get_model('basket', 'Basket')
Partner = get_model('partner', 'Partner')
Country = get_model('address', 'Country')
UserAddress = get_model('address', 'UserAddress')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
Product = get_model('catalogue', 'Product')
Dosimeter = get_model('catalogue', 'Dosimeter')
DefaultProduct = get_model('catalogue', 'DefaultProduct')
ImportOrderObject = get_model('data_import', 'ImportOrderObject')


class ImportOrderSerializer(serializers.Serializer):
    """
    Serializer for importing orders, which were made on partner's sites.

    If data is valid, next objects will be generated:
    - User:
        If `email` is not found in database,
        else will be used exists user.
    - Partner:
        If `partner_code` is not found in database,
        else will be used exists partner.
    - ShippingAddress:
    - BillingAddress:
    - Order:
    - Line:
    - Dosimeters:

    WARNINGS:
        - Check the __init__ method for getting info about non required fields.
    """

    # Prepare choices for convenient using.
    STATUS_CHOICES = Choices(
        *[(s, s, s.title()) for s in settings.OSCAR_ORDER_STATUS_PIPELINE])

    # Partner's fields:
    partner_code = serializers.CharField(allow_blank=True)
    partner_name = serializers.CharField(allow_blank=True)
    partner_order_id = serializers.CharField(allow_blank=True)

    # Order's fields:
    total_incl_tax = serializers.FloatField(allow_null=True, default=0)
    total_excl_tax = serializers.FloatField(allow_null=True, default=0)
    shipping_incl_tax = serializers.FloatField(allow_null=True, default=0)
    shipping_excl_tax = serializers.FloatField(allow_null=True, default=0)
    shipping_id = serializers.CharField(allow_blank=True)
    shipping_code = serializers.CharField(allow_blank=True)
    shipping_method = serializers.CharField(allow_blank=True)
    date_placed = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES, allow_null=True, allow_blank=True)

    # Line's fields:
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(allow_blank=True)

    # Dosimeter's fields:
    serial_numbers = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text=_("Only required if order status is not «Created»."))

    # User's fields:
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)

    # Billing's and Shipping's fields:
    line1 = serializers.CharField(allow_blank=True)
    state = serializers.CharField()
    postcode = serializers.CharField()
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.none())
    owner = serializers.PrimaryKeyRelatedField(queryset=Owner.objects.all())

    # Payment fields
    is_paid = serializers.BooleanField(required=False)
    date_payment = serializers.DateTimeField(required=False)
    report_to_accounting = serializers.BooleanField(required=False)
    invoice_file = serializers.FileField(required=False, allow_null=True)

    # Call source field (turns on/off serial number quantity validation):
    call_source = serializers.CharField(allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = {
            'email', 'product', 'line1', 'state', 'postcode', 'country',
            'quantity', 'owner'}
        for field in set(self.fields) - required_fields:
            self.fields[field].required = False

        # Add to choices only shipping countries.
        self.fields['country'].queryset = Country.objects.filter(
            is_shipping_country=True)

        # Set default values
        self.blank_value = '-'

    def _get_or_create_user(self, validated_data):
        """
        Gets or creates instance of `User`, based on data in the request.
        """

        self.user, created = get_user_model().objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'username': str(uuid4()),
                'first_name': validated_data.get('first_name') or '',
                'last_name': validated_data.get('last_name') or '',
                'phone_number': validated_data.get('phone_number') or ''})
        if created:
            self.user.source = User.SOURCES.imported
            self.user.save()

    def _get_or_create_partner(self, validated_data):
        """
        Gets or creates instance of `Partner`, based on data in the request.
        """
        pass
        # Prevent empty partners in database
        # self.partner, created = Partner.objects.get_or_create(
        #     code=validated_data.get('partner_code') or str(uuid4()),
        #     defaults={'name': validated_data.get('partner_name') or self.blank_value})

    def _create_shipping_address(self, validated_data):
        """
        Creates instance of `ShippingAddress`, based on data in the request.
        """

        # Prepare data.
        data = {
            'first_name': validated_data.get('first_name') or self.blank_value,
            'last_name': validated_data.get('last_name') or self.blank_value,
            'line1': validated_data.get('line1') or self.blank_value,
            'line4': validated_data.get('state') or self.blank_value,
            'state': validated_data.get('state') or self.blank_value,
            'postcode': validated_data.get('postcode'),
            'country': validated_data.get('country').pk,
            'phone_number': validated_data.get('phone_number')}

        # Validate data and create an instance or raise exception.
        shipping_address_form = ShippingAddressForm(data=data)
        if shipping_address_form.is_valid():
            self.shipping_address = shipping_address_form.save()
        else:
            raise ValidationError(shipping_address_form._errors)

    def _create_billing_address(self, validated_data):
        """
        Creates instance of `BillingAddress`, based on data in the request.
        """

        # Prepare data.
        data = {
            'first_name': validated_data.get('first_name') or self.blank_value,
            'last_name': validated_data.get('last_name') or self.blank_value,
            'line1': validated_data.get('line1') or self.blank_value,
            'line4': validated_data.get('state') or self.blank_value,
            'state': validated_data.get('state') or self.blank_value,
            'postcode': validated_data.get('postcode') or self.blank_value,
            'country': validated_data.get('country').pk}

        # Validate data and create an instance or raise exception.
        billing_address_form = BillingAddressForm(data=data)
        if billing_address_form.is_valid():
            self.billing_address = billing_address_form.save()
        else:
            raise ValidationError(billing_address_form._errors)

    def _create_basket(self, validated_data):
        """
        Creates instance of `Basket`, based on data in the request.
        """
        self.basket = Basket.objects.create(
            owner=self.user,
            status=Basket.SUBMITTED,
            date_submitted=validated_data.get('date_placed') or timezone.now())

    def _create_order(self, validated_data):
        """
        Creates instance of `Order`, based on data in the request.
        """

        self.order = Order.objects.create(
            # Relation fields:
            user=self.user,
            site=Site.objects.get_current(),
            billing_address=self.billing_address,
            shipping_address=self.shipping_address,
            basket=self.basket,

            # Flat fields:
            number=OrderNumberGenerator().order_number(self.basket),
            currency=validated_data.get('currency') or settings.OSCAR_DEFAULT_CURRENCY,
            total_incl_tax=validated_data.get('total_incl_tax') or 0,
            total_excl_tax=validated_data.get('total_excl_tax') or 0,
            shipping_incl_tax=validated_data.get('shipping_incl_tax') or 0,
            shipping_excl_tax=validated_data.get('shipping_excl_tax') or 0,
            shipping_method=validated_data.get('shipping_method') or 'Free shipping',
            shipping_code=validated_data.get('shipping_code') or 'free-shipping',
            shipping_id=validated_data.get('shipping_id') or '',
            partner_order_id=validated_data.get('partner_order_id') or '',
            status=validated_data.get('status') or self.STATUS_CHOICES.completed,
            date_placed=validated_data.get('date_placed'),
            owner=validated_data.get('owner'),
            is_paid=validated_data.get('is_paid', False),
            date_payment=validated_data.get('date_payment', None))

    def _create_line(self, validated_data):
        """
        Creates instance of `Line`, based on data in the request.
        """

        upc = validated_data['product'].upc
        quantity = validated_data['quantity'] or 1
        total_incl_tax = validated_data.get('total_incl_tax') or 0
        total_excl_tax = validated_data.get('total_excl_tax') or 0

        partner_fields = {
            'partner': None,
            'partner_name': '',
            'partner_sku': '',
        }
        if hasattr(self, 'partner') and self.partner:
            partner_fields = {
                'partner': self.partner,
                'partner_name': self.partner.name,
                'partner_sku': '%s_%s' % (self.partner.code, upc),
            }

        self.line = Line.objects.create(
            order=self.order,
            partner=partner_fields['partner'],
            partner_name=partner_fields['partner_name'],
            partner_sku=partner_fields['partner_sku'],
            status='created',
            upc=upc,
            quantity=quantity,
            product=validated_data['product'],
            title=validated_data['product'].get_title(),
            unit_cost_price=round(total_incl_tax / quantity, 2),
            unit_price_incl_tax=round(total_incl_tax / quantity, 2),
            unit_price_excl_tax=round(total_excl_tax / quantity, 2),
            line_price_incl_tax=total_incl_tax,
            line_price_excl_tax=total_excl_tax,
            line_price_before_discounts_incl_tax=total_incl_tax,
            line_price_before_discounts_excl_tax=total_excl_tax)

    def _create_dosimeters(self, validated_data):
        """
        Creates instances of `Dosimeter`, based on data in the request.
        """

        # Prepare dosimeters (without saving into db).
        dosimeters = []
        for idx, dosimeter in enumerate(range(validated_data['quantity'])):
            try:
                serial_number = validated_data['serial_numbers'][idx]
            except (TypeError, IndexError, KeyError):
                serial_number = ''

            dosimeters.append(
                Dosimeter(line=self.line, serial_number=serial_number))

        # Create all dosimeters by one request to db.
        self.dosimeters = Dosimeter.objects.bulk_create(dosimeters)

    def _store_request(self, validated_data):
        """
        Creates instance of `ImportOrderObject`, based on data in the request.

        Needed for storing raw and cleaned data for history.
        """
        _params = {
            'indent': 4,
            'sort_keys': True,
            'default': str}

        raw_data = getattr(self.context.get('request'), 'data', {})

        ImportOrderObject.objects.create(
            raw_data=json.dumps(raw_data, **_params),
            cleaned_data=json.dumps(validated_data, **_params))

    def _create_shipment(self, validated_data):
        """
        Tries to get data from delivery API and create an instance of
        `ImportOrderObject`, based on data in the request.
        """
        shipping_id = validated_data.get('shipping_id')
        if shipping_id:
            try:
                # Make a request to delivery service for getting data.
                data = get_shipment_request(shipping_id)
            except django_exceptions.ValidationError:
                # If request is not successfully, use blank data.
                data = {}

            # Create an instance of Shipment model.
            Shipment.objects.create(data=data, order=self.order)

    @transaction.atomic
    def create(self, validated_data):
        """
        This method calls many other methods for creating:
        - User (only when user doesn't exist in our db);
        - Partner (only when partner doesn't exist in our db);
        - ShippingAddress;
        - BillingAddress;
        - Basket;
        - Order;
        - OrderLine(s);
        - Dosimeter(s);

        :return: User instance.
        """

        # Create all needed objects (with relationships).
        self._get_or_create_user(validated_data)
        self._get_or_create_partner(validated_data)
        self._create_shipping_address(validated_data)
        self._create_billing_address(validated_data)
        self._create_basket(validated_data)
        self._create_order(validated_data)
        self._create_line(validated_data)
        self._create_dosimeters(validated_data)
        self._create_shipment(validated_data)
        self._store_request(validated_data)

        if validated_data.get('report_to_accounting'):
            order = self.order
            context = {'order': order}
            serializer = OrderAccountingLedgerSerializer(data=validated_data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Return instance of User.
        return self.user

    @staticmethod
    def validate_serial_numbers(serial_numbers):
        """
        Checks that each serial number is unique (in the request).
        """

        if serial_numbers and len(serial_numbers) != len(set(serial_numbers)):
            raise ValidationError(_('Serial numbers must be unique.'))

        return serial_numbers

    def validate_partner_code(self, partner_code):
        """
        Checks that partner exists.
        """

        if partner_code:
            try:
                self.partner = Partner.objects.get(code=partner_code)
            except Partner.DoesNotExist:
                raise ValidationError(_('Partner was not found.'))

        return partner_code

    def validate(self, attrs):
        """
        Checks that each serial number is unique (in the database).
        Checks that number of serial numbers is the same as quantity.
        """

        attrs = super().validate(attrs)

        serial_numbers = attrs.get('serial_numbers', [])
        quantity = attrs.get('quantity', 0)

        # Validate that number of serial numbers is the same as quantity.
        if attrs.get('call_source', 'web_page') != 'admin_script':
            if attrs.get('status') == self.STATUS_CHOICES.created:
                if len(serial_numbers) != 0:
                    raise ValidationError({'serial_numbers': _('When importing orders with status "created", serial numbers should not be provided.')})
            else:
                if len(serial_numbers) != quantity:
                    raise ValidationError({'serial_numbers': _('Number of serial numbers must be the same as quantity.')})

        # Validate that serial numbers is not existing in the database yet.
        product = attrs.get('product')
        if product and serial_numbers:
            not_unique_serial_numbers = []
            product_class_name = product.product_class.name

            # Validation for `DefaultProduct`.
            if product_class_name == settings.OSCAR_PRODUCT_TYPE_DEFAULT:
                not_unique_serial_numbers = DefaultProduct.objects.filter(
                    serial_number__in=serial_numbers
                ).values_list('serial_number', flat=True)

            # Validation for `Dosimeter`.
            elif product_class_name == settings.OSCAR_PRODUCT_TYPE_DOSIMETER:
                not_unique_serial_numbers = Dosimeter.objects.filter(
                    serial_number__in=serial_numbers
                ).values_list('serial_number', flat=True)

            # If serial_numbers were found add new error into errors:
            if not_unique_serial_numbers:
                numbers = ', '.join(str(sn) for sn in not_unique_serial_numbers)
                msg = _('Next serial numbers already exists in the database: %s.') % numbers
                raise ValidationError({'serial_numbers': msg})

        return attrs

    def to_representation(self, instance):
        return {
            'user_id': self.user.id,
            'shipping_address_id': self.shipping_address.id,
            'billing_address_id': self.billing_address.id,
            'order_id': self.order.id,
            'line_id': self.line.id,
            'dosimeters': [str(d.id) for d in self.dosimeters]}


class ImportAppSerializer(serializers.Serializer):
    """
    Serializer for importing apps,
    which will be available for downloading on the website.
    """

    OS_CHOICES = (
        ('android', _('Android')),
        ('ios', _('iOS')))

    os = serializers.ChoiceField(choices=OS_CHOICES)
    app = serializers.FileField()

    def create(self, validated_data):

        # Generate sub directory.
        sub_dir = 'downloads/apps/%s/' % validated_data['os']

        # Generate `filename` and `path`.
        name, ext = os.path.splitext(validated_data['app'].name)
        filename = slugify(name)
        path = os.path.join(settings.MEDIA_ROOT, sub_dir, filename + ext)

        # Try to find and remove exists file (by `path`).
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

        # Save new file.
        default_storage.save(path, ContentFile(validated_data['app'].read()))

        # Generate and add `url` field with link
        # for downloading file into `validated_data`.
        validated_data['url'] = '%s%s%s' % (
            settings.MEDIA_URL,
            sub_dir,
            filename + ext)

        # Create and return instance.
        return type('UploadedApplication', (object,), validated_data)
