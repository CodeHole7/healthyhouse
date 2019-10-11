# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import get_connection
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User

class Owner(models.Model):
    """
    Model for order's owner.

    Order has a foreign key to Order.
    """

    first_name = models.CharField(_('First name'), max_length=255)
    last_name = models.CharField(_('Last name'), max_length=255)
    email = models.EmailField(_('Email address'), blank=True)
    is_default = models.BooleanField(_('Is default'), default=False)
    user = models.ForeignKey(User, verbose_name ="Staff", default=1)

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_from_email(self):
        if hasattr(self, 'email_config'):
            return self.email_config.from_email
        return settings.DEFAULT_FROM_EMAIL

    def get_connection(self):
        if hasattr(self, 'email_config'):
            return self.email_config.get_connection()

    @staticmethod
    def validate_is_default(instance, is_default):
        if not is_default:
            qs = Owner.objects.filter(is_default=True)
            if instance and instance.id:
                qs = qs.exclude(id=instance.id)
            if not qs.exists():
                raise ValidationError(_('One owner should be default.'))
        return is_default

    @staticmethod
    def default_owner():
        return Owner.objects.filter(is_default=True).first()


class OwnerPDFReportTheme(models.Model):
    pdf_template = models.TextField(
        _('Template'))
    owner = models.OneToOneField(
        Owner, verbose_name=_('Owner'), related_name='report_template')
    logo = models.ImageField(
        _('Logo'), blank=True, null=True)

    class Meta:
        ordering = ('owner_id', )

    def __str__(self):
        return f'Report template for owner_id={self.owner_id}'


class OwnerEmailConfig(models.Model):
    owner = models.OneToOneField(Owner, related_name='email_config')
    from_email = models.EmailField(_('Default from email address'))
    username = models.CharField(_('Username'), max_length=100)
    password = models.CharField(_('Password'), max_length=100)
    host = models.CharField(
        _('Host'), max_length=100, default='smtp.mail.eu-west-1.awsapps.com')
    port = models.PositiveSmallIntegerField(
        _('Port'), validators=[MaxValueValidator(999)], default=465)
    use_ssl = models.BooleanField(_('Use ssl?'), default=True)
    use_tsl = models.BooleanField(_('Use tsl?'), default=False)

    def get_connection(self):
        connection = get_connection(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tsl,
            # fail_silently=True,
            use_ssl=self.use_ssl
        )
        return connection
