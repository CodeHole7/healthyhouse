from uuid import uuid4

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from oscar.core.compat import get_user_model

User = get_user_model()


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'is_active',
            'is_partner', 'is_laboratory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            qs = User.objects.all()
            if self.instance and self.instance.id:
                qs = User.objects.exclude(id=self.instance.id)

            has_other_user = qs.filter(email__iexact=email).exists()
            if has_other_user:
                raise ValidationError(_('User with this email already exists.'))
        return email

    def save(self, commit=True):
        if not self.instance.id:
            self.instance.username = str(uuid4())
            self.instance.source = User.SOURCES.dashboard
        return super().save(commit)
