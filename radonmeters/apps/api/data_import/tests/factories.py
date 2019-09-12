import random

import factory
import factory.fuzzy
from django.conf import settings
from django.utils.text import slugify
from faker import Faker
from oscar.test.factories import CountryFactory, PartnerFactory

from owners.tests.factories import OwnerFactory

fake = Faker()


class DataImportDictFactory(factory.DictFactory):
    """
    Factory for generating dict with faked data for
    checks of importing functionality.
    """

    # partner_name = fake.company()
    # partner_code = slugify(partner_name)
    partner_code = factory.lazy_attribute(lambda x: PartnerFactory().code)
    partner_order_id = fake.ean8()
    total_incl_tax = round(random.randint(0, 1000) * 1.33, 2)
    total_excl_tax = round(total_incl_tax * 0.85, 2)
    shipping_incl_tax = round(random.randint(0, 1000) * 1.33, 2)
    shipping_excl_tax = round(shipping_incl_tax * 0.85, 2)
    #shipping_id = fake.ean8()
    shipping_code = 'free_shipping'
    shipping_method = 'Free shipping'
    date_placed = fake.date_time_this_year().strftime('%d-%m-%Y %H:%m')
    status = random.choice(list(settings.OSCAR_ORDER_STATUS_PIPELINE.keys() - {'created'}))
    quantity = random.randint(1, 20)
    owner = factory.lazy_attribute(lambda x: OwnerFactory().id)
    currency = fake.currency_code()
    email = fake.email()
    phone_number = factory.lazy_attribute(lambda x: '+45505050%s' % random.randint(10, 99))
    first_name = fake.first_name()
    last_name = fake.last_name()
    line1 = fake.street_address()
    state = fake.state()
    country = factory.lazy_attribute(lambda x: CountryFactory(iso_3166_1_a2='DK').pk)
    postcode = factory.lazy_attribute(lambda x: str(random.randint(5000, 5500)))
    serial_numbers = [str(fake.uuid4()) for _ in range(quantity)]
