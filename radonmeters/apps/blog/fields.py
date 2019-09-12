from django import forms
from zinnia.admin.fields import MPTTModelChoiceIterator
from zinnia.admin.fields import MPTTModelMultipleChoiceField


class CustomMPTTModelChoiceIterator(MPTTModelChoiceIterator):
    """
    Overwritten because default realisation is not working with Django 1.11+.

    Replaces return of `choice` method.
    """

    def choice(self, obj):
        return super(MPTTModelChoiceIterator, self).choice(obj)


class CustomMPTTModelMultipleChoiceField(MPTTModelMultipleChoiceField):
    """
    Overwritten because default realisation is not working with Django 1.11+.

    Uses `CustomMPTTModelChoiceIterator` instead `MPTTModelChoiceIterator`.
    """

    def _get_choices(self):
        """
        Override the _get_choices method to use MPTTModelChoiceIterator.
        """
        return CustomMPTTModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)
