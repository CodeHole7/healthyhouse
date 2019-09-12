from django.contrib.postgres.fields.jsonb import JSONField
from model_utils.models import TimeStampedModel

from common.models import UUIDAbstractModel


class ImportOrderObject(
        UUIDAbstractModel,
        TimeStampedModel):
    """
    Model for storing successful requests on import data.
    """

    raw_data = JSONField()
    cleaned_data = JSONField()
