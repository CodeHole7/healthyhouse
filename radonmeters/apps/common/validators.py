from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class PhoneNumberValidator(RegexValidator):
    """
    Checks that value it's a valid phone number (E.164 Format).
    """
    code = 'invalid_format'
    regex = r'^\+?1?\d{9,15}$'
    message = _('Phone number must be entered in the format: "+999999999". '
                'Up to 15 digits allowed.')
