from uuid import uuid4
from django.utils.translation import ugettext_lazy as _

from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'is_active', 'is_partner', 'is_laboratory', 'source']
        read_only_fields = ['source']
        extra_kwargs = {
            'email': {
                'required': True,
            },
        }

    def save(self, **kwargs):
        if not self.instance:
            kwargs['source'] = User.SOURCES.imported
            kwargs['username'] = str(uuid4())
        return super().save(**kwargs)

    def validate_email(self, email):
        # TODO union with dashboard forms
        if email:
            email = email.lower()
            qs = User.objects.all()
            if self.instance and self.instance.id:
                qs = User.objects.exclude(id=self.instance.id)

            has_other_user = qs.filter(email__iexact=email).exists()
            if has_other_user:
                raise serializers.ValidationError(_('User with this email already exists.'))
        return email
