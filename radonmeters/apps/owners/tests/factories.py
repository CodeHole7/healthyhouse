import factory

from owners.models import Owner
from owners.models import OwnerEmailConfig


# from users.models import User
from oscar.test.factories.customer import UserFactory

class OwnerFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: 'owner%s@email.com' % n)
    user = factory.SubFactory(UserFactory)
    class Meta:
        model = Owner


class OwnerEmailConfigFactory(factory.DjangoModelFactory):
    owner = factory.SubFactory(OwnerFactory)
    from_email = factory.Sequence(lambda n: 'owner%s@email.com' % n)
    username = factory.Sequence(lambda n: 'username%s' % n)
    password = factory.Sequence(lambda n: 'password%s' % n)
    host = 'consolemail'

    class Meta:
        model = OwnerEmailConfig
