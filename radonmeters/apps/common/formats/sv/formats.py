# Update requested date formats

from django.conf import settings
DATE_FORMAT = settings.DATE_FORMAT
DATETIME_FORMAT = settings.DATETIME_FORMAT
DATE_INPUT_FORMATS = [settings.DATE_FORMAT_REST]
DATETIME_INPUT_FORMATS = [settings.DATETIME_FORMAT_REST, '%d-%m-%Y', "%Y-%m-%d %H:%M"]
SHORT_DATE_FORMAT = settings.SHORT_DATE_FORMAT
SHORT_DATETIME_FORMAT = settings.SHORT_DATETIME_FORMAT
