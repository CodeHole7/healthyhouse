from django.utils import timezone
from django.utils.translation import ugettext as _
from oscar.core.loading import get_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from sorl.thumbnail import get_thumbnail

from api.serializers import ValidateWithCleanSerializerMixin
from common.utils import custom_format_currency

ProductClass = get_model('catalogue', 'ProductClass')
Product = get_model('catalogue', 'Product')
Dosimeter = get_model('catalogue', 'Dosimeter')
DefaultProduct = get_model('catalogue', 'DefaultProduct')
Location = get_model('catalogue', 'Location')
Line = get_model('order', 'Line')


class OrderedProductAbstractSerializer(serializers.ModelSerializer):
    """
    Abstract serializer for providing common fields and methods.
    """

    product_title = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    @staticmethod
    def get_product_title(instance) -> str:
        """
        Tries to get and return title of product.
        """
        if isinstance(instance, Line):
            return instance.product.get_title()
        elif isinstance(instance, Dosimeter):
            return instance.line.product.get_title()
        else:
            raise NotImplementedError('This type is not supported.')

    @staticmethod
    def get_product_price(instance) -> str:
        """
        Tries to get and return price of product.
        """
        if isinstance(instance, Line):
            value = instance.line_price_incl_tax
        elif isinstance(instance, Dosimeter):
            value = instance.line.line_price_incl_tax / instance.line.quantity
        else:
            raise NotImplementedError('This type is not supported.')
        return custom_format_currency(number=value)

    @staticmethod
    def get_product_image(instance) -> str or None:
        """
        Tries to get, make thumbnail and return of `primary_image` of product.
        """

        # Try to get `primary_image` of product.
        if isinstance(instance, Line):
            primary_image = instance.product.primary_image()
        elif isinstance(instance, Dosimeter):
            primary_image = instance.line.product.primary_image()
        else:
            raise NotImplementedError('This type is not supported.')

        # Try to make a thumbnail if `primary_image` is existing.
        if hasattr(primary_image, 'original'):
            return get_thumbnail(
                primary_image.original, '70x70', crop='center', quality=99).url


class OrderedProductDefaultSerializer(OrderedProductAbstractSerializer):
    """
    Serializer for representation products with product class = Default.

    Structure example:
    {
        "product_title": "string",
        "product_price": "string",
        "product_image": "string|null"
        "quantity": "int",
    }
    """

    class Meta:
        model = Line
        fields = (
            'id', 'product_title', 'product_price', 'product_image',
            'quantity')


class OrderedProductDosimeterSerializer(OrderedProductAbstractSerializer):
    """
    Serializer for representation products with product class = Dosimeter.

    Structure example:
    {
        "pk": "string",
        "url": "string",

        "product_title": "string",
        "product_price": "string",
        "product_image": "string|null",

        "serial_number": "string|null",
        "concentration": "string|null",
        "uncertainty": "string|null",
        "yearly_avg": "string|null",

        "is_active": "boolean|null",
        "measurement_start_date": "string|null",
        "measurement_end_date": "string|null",
        "floor": "int|null",
        "location": "string|null",
    }
    """

    url = serializers.ReadOnlyField(source='get_absolute_url')
    product_title = serializers.ReadOnlyField(source='line.product.get_title')
    status = serializers.ReadOnlyField(source='get_status_as_dict')

    serial_number = serializers.ReadOnlyField(source='get_serial_number')

    concentration = serializers.ReadOnlyField(source='concentration_visual')
    uncertainty = serializers.ReadOnlyField(source='uncertainty_visual')
    yearly_avg = serializers.ReadOnlyField(source='avg_concentration_visual')

    is_active = serializers.BooleanField(required=False)
    measurement_start_date = serializers.DateField(required=False)
    measurement_end_date = serializers.DateField(required=False)
    floor = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False)

    class Meta:
        model = Dosimeter
        fields = (
            'pk',  'url', 'status',

            'product_title', 'product_price', 'product_image',

            'serial_number', 'concentration', 'uncertainty', 'yearly_avg',

            'is_active', 'measurement_start_date', 'measurement_end_date', 'floor',
            'location')

    def update(self, instance, validated_data):
        instance.last_modified_date = timezone.now()
        instance.last_modified_by = self.context['request'].user
        result = super().update(instance, validated_data)
        # Update weirdness status of the corresponding order.
        instance.line.order.update_weirdness_statuses()
        instance.line.order.not_weird = False
        instance.line.order.not_weird_explanation = ''
        # Update approval status of the corresponding order.
        instance.line.order.is_approved = False
        instance.line.order.save()
        return result

    def validate(self, attrs):
        data = super().validate(attrs)

        # Check that `start_date` less or equal with `end_date`.
        start_date = attrs.get('measurement_start_date')
        end_date = attrs.get('measurement_end_date')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                _('Start date cannot be greater than the end date.'))

        return data


class InstructionDosimeterSerializer(OrderedProductDosimeterSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        instruction = self.context['instruction']
        return reverse(
            'api:instructions:instruction-dosimeters-detail',
            kwargs={
                'pk': instruction.pk,
                'dosimeter_pk': obj.pk})


class DosimeterChangeSerializer(
        ValidateWithCleanSerializerMixin,
        serializers.ModelSerializer):
    """
    Serializer for creating/changing instances of `catalogue.Dosimeter`.
    """

    class Meta:
        model = Dosimeter
        fields = ('serial_number',)


class DefaultProductChangeSerializer(
        ValidateWithCleanSerializerMixin,
        serializers.ModelSerializer):
    """
    Serializer for creating/changing instances of `catalogue.DefaultProduct`.
    """

    class Meta:
        model = DefaultProduct
        fields = ('serial_number',)


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ('id', 'name')
