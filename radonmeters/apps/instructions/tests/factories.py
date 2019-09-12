import factory

from instructions.models import InstructionImage
from instructions.models import InstructionTemplate
from instructions.models import Instruction


class InstructionImageFactory(factory.DjangoModelFactory):
    image = factory.django.ImageField()

    class Meta:
        model = InstructionImage


class InstructionTemplateFactory(factory.DjangoModelFactory):
    pdf_template = 'Text'

    class Meta:
        model = InstructionTemplate
