from rest_framework import serializers


class ValidateWithCleanSerializerMixin:
    """
    Mixin for adding call of model's clean method.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if not isinstance(self, serializers.ModelSerializer):
            raise NotImplementedError(
                'This mixin can be used only with '
                'instances of ModelSerializer.')

    def validate(self, attrs):
        """
        Calls model's clean method.
        """

        # Get all previously changes.
        attrs = super().validate(attrs)

        # Call model's clean method.
        if self.instance is not None:
            for k, v in attrs.items():
                setattr(self.instance, k, v)
            self.instance.clean()
        else:
            instance = self.Meta.model(**attrs)
            instance.clean()

        # Return attrs, if clean method didn't raise ValidationError.
        return attrs
