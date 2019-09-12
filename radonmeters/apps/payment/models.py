from oscar.apps.payment.abstract_models import AbstractSource
from oscar.apps.payment.abstract_models import AbstractSourceType


class SourceType(AbstractSourceType):
    pass


class Source(AbstractSource):
    pass


# noinspection PyUnresolvedReferences
from oscar.apps.payment.models import *
