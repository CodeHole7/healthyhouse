import factory
from factory.fuzzy import FuzzyDate
from factory.fuzzy import FuzzyInteger
from django.utils import timezone
from oscar.core.loading import get_model


class DosimeterFactory(factory.DjangoModelFactory):
    """ Represent Dosimeter instance """

    serial_number = factory.Sequence(lambda n: "number_{}".format(n))
    line = factory.SubFactory('oscar.test.factories.order.OrderLineFactory')
    measurement_start_date = FuzzyDate(
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timezone.timedelta(days=20))
    measurement_end_date = FuzzyDate(
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timezone.timedelta(days=25))
    floor = FuzzyInteger(10)
    location = factory.Sequence(lambda n: "room_{}".format(n))

    class Meta:
        model = get_model('catalogue', 'Dosimeter')
        django_get_or_create = ('serial_number',)
