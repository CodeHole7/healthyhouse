import factory.fuzzy
from faker import Faker
from oscar.test.factories import UserFactory

from instructions.models import InstructionImage, Instruction

fake = Faker()


class InstructionImageFactory(factory.django.DjangoModelFactory):
    image = factory.django.ImageField()

    class Meta:
        model = InstructionImage


class InstructionFactory(factory.django.DjangoModelFactory):
    pdf_file = factory.django.FileField()
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Instruction

    @factory.post_generation
    def orders(self, create, extracted, **kwargs):
        if create and extracted:
            self.orders.add(*extracted)
