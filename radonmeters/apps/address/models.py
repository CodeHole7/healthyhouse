from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.address.abstract_models import AbstractUserAddress

from common.validators import PhoneNumberValidator


class MunicipalityRadonRisk(models.Model):
    """
    Model for storing radon risk level for municipalities.
    """
    avglevel = models.IntegerField(
        verbose_name=_('Avg level'),
        default=0)
    level = models.IntegerField(
        verbose_name=_('Level'),
        default=0)
    municipality = models.CharField(
        verbose_name=_('Municipality'),
        max_length=255,
        unique=True)

    def __str__(self):
        return '{}: municipality radon risk {}, avg = {}'.format(
            self.municipality, self.level, self.avglevel)


class UserAddress(AbstractUserAddress):
    """
    Overridden for replacing field `phone_number` with custom realisation.
    """
    phone_number = models.CharField(
        _('Phone Number'),
        help_text=_('Phone number in the international format.'),
        max_length=15, validators=[PhoneNumberValidator()], blank=True)


# noinspection PyUnresolvedReferences
from oscar.apps.address.models import *
