from oscar.core.loading import get_model
from rest_framework import serializers

Owner = get_model('owners', 'Owner')


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Owner
        fields = ['id', 'first_name', 'last_name', 'email', 'is_default', 'user']

    def validate_is_default(self, is_default):
        return Owner.validate_is_default(self.instance, is_default)
