from oscar.core.loading import get_model
from rest_framework import serializers

ShippingAddress = get_model('order', 'ShippingAddress')


class ShippingAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for providing shipping address data for delivery system.

    WARNINGS:
    - `email` field should be provided separately.
    """

    address1 = serializers.ReadOnlyField(source='get_address')
    address2 = serializers.ReadOnlyField(default=None)
    country_code = serializers.ReadOnlyField(source='country.code')
    zipcode = serializers.ReadOnlyField(source='postcode')
    city = serializers.ReadOnlyField(source='get_city')
    attention = serializers.ReadOnlyField(default=None)
    telephone = serializers.ReadOnlyField(source='phone_number')
    mobile = serializers.ReadOnlyField(source='phone_number')
    instruction = serializers.ReadOnlyField(default=None)

    class Meta:
        model = ShippingAddress
        fields = (
            'name', 'address1', 'address2', 'country_code', 'zipcode', 'city',
            'attention', 'telephone', 'mobile', 'instruction')


class ShippingAddressDeliverSerializer(ShippingAddressSerializer):
    # override country code as UPPERCASE
    country_code = serializers.SerializerMethodField()

    def get_country_code(self, obj):
        return obj.country.code.upper()
