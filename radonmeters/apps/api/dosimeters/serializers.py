from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_model
from rest_framework import serializers

Dosimeter = get_model('catalogue', 'Dosimeter')
OrderLine = get_model('order', 'Line')
OrderOrder = get_model('order', 'Order')
Batch = get_model('catalogue', 'Batch')

class IntegerSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    
class DosimeterSerialNumberSerializer(serializers.Serializer):
    serial_number = serializers.CharField()

    def validate_serial_number(self, serial_number):
        try:
            self.dosimeter = Dosimeter.objects.get(serial_number=serial_number)
        except Dosimeter.DoesNotExist:
            raise serializers.ValidationError(_('Dosimeter was not found.'))
        return serial_number

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['dosimeter_id'] = self.dosimeter.id
        order_line = OrderLine.objects.get(id=self.dosimeter.line_id)
        order_order = OrderOrder.objects.get(id=order_line.order_id)
        representation['order_number']=order_order.number
        return representation

class DosimeterChangeSerializer(serializers.ModelSerializer):
    """  Serializer for changing any data of Dosimeters. """

    concentration_visual = serializers.ReadOnlyField()
    uncertainty_visual = serializers.ReadOnlyField()
    avg_concentration_visual = serializers.ReadOnlyField()

    class Meta:
        model = Dosimeter
        fields = (
            'serial_number',
            'status',

            'concentration_visual',
            'uncertainty_visual',
            'avg_concentration_visual',
            'active_area',
            'is_active',
            'use_raw_concentration',

            'concentration',
            'uncertainty',
            'measurement_start_date',
            'measurement_end_date',
            'floor',
            'location')

    def get_user(self):
        return self.context['request'].user

    def update(self, instance, validated_data):
        instance.last_modified_date = timezone.now()
        instance.last_modified_by = self.get_user()
        result = super().update(instance, validated_data)
        # Update weirdness status of the corresponding order.
        instance.line.order.update_weirdness_statuses()
        instance.line.order.not_weird = False
        instance.line.order.not_weird_explanation = ''
        # Update approval status of the corresponding order.
        instance.line.order.is_approved = False
        # Update status of the corresponding order.
        instance.line.order.update_status()
        # Save the corresponding order.
        instance.line.order.save() 
        return result


class DosimeterChangeInstructionSerializer(DosimeterChangeSerializer):

    def get_user(self):
        return self.context.get('user')


class DosimeterUpdateSerializer(serializers.ModelSerializer):
    """  Serializer for updating data of Dosimeters via laboratory's requests. """

    id = serializers.CharField()
    language = serializers.ChoiceField(
        required=False, choices=settings.LANGUAGES)

    class Meta:
        model = Dosimeter
        fields = ('id', 'concentration', 'uncertainty', 'language')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = {'id'}
        for field in set(self.fields) - required_fields:
            self.fields[field].required = False

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ('id', 'batch_description','batch_owner_id' )

class DosimeterUpdateStatusSerializer(serializers.ModelSerializer):
    """  Serializer for updating Dosimeter status """

    owner_id = serializers.CharField(required=False)
    class Meta:
        model = Dosimeter
        fields = ('serial_number', 'status', 'owner_id')

    def validate_serial_number(self, serial_number):
        try:
            self.dosimeter = Dosimeter.objects.get(serial_number=serial_number)
        except Dosimeter.DoesNotExist:
            raise serializers.ValidationError(_('Dosimeter was not found.'))
        return serial_number

