from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from rest_framework import serializers

User = get_user_model()

InstructionImage = get_model('instructions', 'InstructionImage')
Instruction = get_model('instructions', 'Instruction')


class InstructionImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = InstructionImage
        fields = ['id', 'image']
        read_only_fields = ['id']
