# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.db import transaction
from oscar.core.loading import get_model
from rest_framework import serializers
from rest_framework.reverse import reverse

from accounting.models import AccountingLedgerItem
from accounting.utils import AccountingSync
from api.catalogue.serializers import OrderedProductDefaultSerializer
from api.catalogue.serializers import InstructionDosimeterSerializer
from api.catalogue.serializers import OrderedProductDosimeterSerializer
from common.utils import custom_format_currency

Dosimeter = get_model('catalogue', 'Dosimeter')
DefaultProduct = get_model('catalogue', 'DefaultProduct')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
ShippingAddress = get_model('order', 'ShippingAddress')
BillingAddress = get_model('order', 'BillingAddress')


class CustomerOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for representation Order object to customer.

    Response example:
    [
        {
            ...
            "products": {
                "defaults": [
                    <OrderedProductDefaultSerializer>,
                ],
                "dosimeters": [
                    <OrderedProductDosimeterSerializer>,
                ]
            }
        }
    ]
    """

    total_price = serializers.SerializerMethodField()
    date_placed = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    generate_dosimeter_report_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'number', 'date_placed', 'total_price', 'status',
            'products', 'generate_dosimeter_report_url')

    @staticmethod
    def get_total_price(instance):
        """
        Returns formatted string, for example: "215.99 DKK".
        """

        return custom_format_currency(
            number=instance.total_incl_tax,
            currency=instance.currency)

    @staticmethod
    def get_date_placed(instance):
        """
        Return date instead of datetime
        """
        return instance.date_placed.strftime(settings.DATE_FORMAT_REST)

    @staticmethod
    def get_product_serializer():
        return OrderedProductDefaultSerializer

    @staticmethod
    def get_dosimeter_serializer():
        return OrderedProductDosimeterSerializer

    def get_products(self, instance):
        """
        Returns dictionary, for example: look docstring of class.
        """

        # Get all lines from prefetched data.
        lines = instance.lines.all()

        # Group lines by product classes.
        default_slug = settings.OSCAR_PRODUCT_TYPE_DEFAULT.lower()
        lines_with_default_products = [
            l for l in lines if l.product.product_class.slug == default_slug]

        dosimeter_slug = settings.OSCAR_PRODUCT_TYPE_DOSIMETER.lower()
        lines_with_dosimeter_products = [
            l for l in lines if l.product.product_class.slug == dosimeter_slug]

        # TODO: This should be optimized.
        dosimeters = Dosimeter.objects.filter(
            line__in=lines_with_dosimeter_products)

        # Serialize and return data.
        context = self.context
        return {
            'defaults': self.get_product_serializer()(
                lines_with_default_products, many=True, context=context).data,
            'dosimeters': self.get_dosimeter_serializer()(
                dosimeters, many=True, context=context).data}

    def get_generate_dosimeter_report_url(self, instance):
        """
        :param instance:
        :return: report url
        """
        return reverse(
            'api:orders:order-generate-pdf-report',
            kwargs={'pk': instance.pk})


class CustomerInstructionOrderSerializer(CustomerOrderSerializer):

    def get_generate_dosimeter_report_url(self, instance):
        """
        :param instance:
        :return: report url
        """

        instruction = self.context['instruction']
        return reverse(
            'api:instructions:instruction-generate-pdf-report',
            kwargs={
                'pk': instruction.pk,
                'order_pk': instance.pk})

    @staticmethod
    def get_dosimeter_serializer():
        return InstructionDosimeterSerializer


class AbstractAddressSerializer(serializers.ModelSerializer):
    """
    Abstract serializer for representation fields of AbstractAddress instances.
    """

    class Meta:
        fields = (
            'title', 'first_name', 'last_name',
            'line1', 'line2', 'line3', 'line4',
            'state', 'postcode', 'country')


class ShippingAddressSerializer(AbstractAddressSerializer):
    """
    Serializer for representation ShippingAddress instances.
    """

    class Meta:
        model = ShippingAddress
        fields = [*AbstractAddressSerializer.Meta.fields, 'phone_number']


class BillingAddressSerializer(AbstractAddressSerializer):
    """
    Serializer for representation BillingAddress instances.
    """

    class Meta:
        model = BillingAddress
        fields = AbstractAddressSerializer.Meta.fields


class LineItemSerializer(serializers.ModelSerializer):
    """
    Dynamic serializer for items of instance of Line.
    """

    class Meta:
        model = None
        fields = ('id', 'serial_number')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.Meta.model == Dosimeter:
            data['item_type'] = 'dosimeter'
        elif self.Meta.model == DefaultProduct:
            data['item_type'] = 'default_product'
        return data


class LineSerializer(serializers.ModelSerializer):
    """
    Serializer for representation Line instances.
    """

    items = serializers.SerializerMethodField()

    class Meta:
        model = Line
        fields = ['id', 'title', 'upc', 'quantity', 'items']

    def get_items(self, instance):
        """
        Returns list of items for current line.
        """

        # Response for dosimeters.
        dosimeters = instance.dosimeters.all()
        if dosimeters:
            serializer = LineItemSerializer
            serializer.Meta.model = Dosimeter
            return serializer(dosimeters, many=True, context=self.context).data

        # Response for default products.
        products = instance.products.all()
        if products:
            serializer = LineItemSerializer
            serializer.Meta.model = DefaultProduct
            return serializer(products, many=True, context=self.context).data


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer represents common data of Order instance.
    """

    quantity = serializers.ReadOnlyField(source='num_items')
    date_placed = serializers.SerializerMethodField()
    approved_date = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'status', 'date_placed', 'quantity',
            'shipping_code', 'shipping_id', 'owner', 'is_reported_by_partner',
            'is_report_sent', 'is_approved', 'user_who_approved',
            'approved_date', 'sent_date',
            'is_exists_accounting', 'is_paid', 'date_payment']

        read_only_fields = [
            'is_report_sent', 'is_approved', 'user_who_approved',
            'approved_date', 'sent_date', 'is_exists_accounting']

    @staticmethod
    def get_date_placed(instance):
        """
        Return date instead of datetime
        """
        return instance.date_placed.strftime(settings.DATE_FORMAT_REST)

    @staticmethod
    def get_approved_date(instance):
        """
        Return date instead of datetime
        """
        if instance.approved_date:
            return instance.approved_date.strftime(settings.DATE_FORMAT_REST)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        # update representation of date_payment
        if 'date_payment' in result and instance.date_payment:
            result['date_payment'] = instance.date_payment.strftime(settings.DATE_FORMAT_REST)
        return result


class OrderDetailSerializer(OrderListSerializer):
    """
    Serializer represents all data of Order instance (with products).
    """

    email = serializers.ReadOnlyField(source='user.email')
    phone_number = serializers.ReadOnlyField(source='user.phone_number')
    shipping_address = ShippingAddressSerializer(read_only=True)
    shipping_code = serializers.ReadOnlyField(source='shipping_id')
    billing_address = BillingAddressSerializer(read_only=True)
    lines = LineSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField()
    date_placed = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'lines', 'number', 'status', 'quantity', 'currency',
            'date_placed', 'email', 'phone_number',
            'billing_address', 'shipping_address', 'shipping_code',
            'shipping_id', 'shipping_incl_tax', 'shipping_method',
            'total_price', 'total_excl_tax', 'total_incl_tax',
            'is_reported_by_partner',
            'is_report_sent', 'sent_date', 'is_approved', 'user_who_approved',
            'approved_date',
            'is_exists_accounting', 'is_paid', 'date_payment']
        read_only_fields = [
            'is_report_sent', 'sent_date', 'is_approved', 'user_who_approved',
            'approved_date', 'is_exists_accounting']

    @staticmethod
    def get_total_price(instance):
        """
        Returns formatted string, for example: "215.99 DKK".
        """

        return custom_format_currency(
            number=instance.total_incl_tax,
            currency=instance.currency)
    
    @staticmethod
    def validate_number(self, number):
        try:
            self.order = Order.objects.get(number=number)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order Number is not correct.')
        return number



class OrderApproveSerializer(serializers.ModelSerializer):
    """
    Serializer represents order after approving
    """
    user_who_approved = serializers.EmailField(
        source='user_who_approved.email')
    approved_date = serializers.SerializerMethodField()
    not_weird_explanation = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'is_approved', 'user_who_approved', 'approved_date', 'not_weird_explanation']

    def get_approved_date(self, obj):
        return obj.approved_date.strftime(settings.DATE_FORMAT_REST)


class OrderAccountingLedgerSerializer(serializers.ModelSerializer):
    invoice_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = AccountingLedgerItem
        fields = ['invoice_file']

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        invoice_file = validated_data.pop('invoice_file', None)
        acc_sync = AccountingSync()
        order = self.context['order']
        try:
            print('======= trying AccounttingSync.post_invoice_metadata ========')
            response_sync = acc_sync.post_invoice_metadata(order, invoice_file)
        except Exception as e:
            raise serializers.ValidationError('Error during importing file %s' % e)
        
        print('\n================= Accounting Legder Serializer ======================')
        print(order)
        print('======================================================\n\n')
        
        self.metadata = json.loads(response_sync.text)[0]
        self.external_id = self.metadata.get('Id')
        if not self.external_id:
            raise serializers.ValidationError('External_id is required!')
        return validated_data

    def save(self, **kwargs):
        with transaction.atomic():
            kwargs['order'] = self.context['order']
            kwargs['external_id'] = self.external_id
            kwargs['metadata'] = self.metadata
            instance = super().save(**kwargs)
            order = instance.order
            order.is_exists_accounting = True
            order.save()
            return instance

class OrderExternalReportSerializer(serializers.ModelSerializer):
    external_report_pdf = serializers.FileField(required=True)

    class Meta:
        model = Order
        fields = ['external_report_pdf']

    def validate_external_report_pdf(self, value):
        """
        Check whether uploaded file is a PDF file.
        """
        if value.content_type != 'application/pdf':
            raise serializers.ValidationError('External PDF report should be a file in PDF format!')
        # Quick check if file is non-pdf
        for chunk in value.chunks():
            if chunk[0:4] != b'%PDF':
                raise serializers.ValidationError('External PDF report should be a file in PDF format!')
            break
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            instance = super().save(**kwargs)
            instance.use_external_report = True
            instance.save()
            return instance

class OrderShipmentSerializer(serializers.ModelSerializer):
    """  Serializer for create shipment """
    number = serializers.CharField()
    class Meta:
        model = Order
        fields = ('number',)
    def validate_number(self, number):
        try:
            self.order = Order.objects.get(number=number)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order Number is not correct.')
        return number


class OrderDosimeterDetailSerializer(serializers.ModelSerializer):
    """  Serializer for one order """
    id = serializers.ReadOnlyField()
    number = serializers.CharField()
    status = serializers.ReadOnlyField()#CharField(required=False)
    lines = LineSerializer(read_only=True, many=True)
    quantity = serializers.ReadOnlyField(source='num_items')
    class Meta:
        model = Order
        fields = ('id', 'number', 'status','quantity','lines', 'owner_id')
    def validate_number(self, number):
        try:
            self.order = Order.objects.get(number=number)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order Number is not correct.')
        return number

class OrderUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for update order status in API """
    number = serializers.CharField()
    status = serializers.CharField()
    owner = serializers.IntegerField()
    class Meta:
        model = Order
        fields = [
            'id', 'number', 'status', 'owner',]
    def validate_number(self, number):
        try:
            self.order = Order.objects.get(number=number)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order Number is not correct.')
        return number