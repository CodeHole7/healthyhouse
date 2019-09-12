from uuid import uuid4

from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from common.utils import get_protocol


class UUIDAbstractModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class SubscribeRequest(UUIDAbstractModel, TimeStampedModel):
    """
    Model for saving emails from `SubscribeRequestForm` in the database.
    """

    # TODO: Need to add invent and handler for rejecting attacks!!!

    email = models.EmailField(_('Email address'), max_length=255, unique=True)


class ConsultationRequest(UUIDAbstractModel, TimeStampedModel):
    """
    Model for saving emails from `ConsultationRequestForm` in the database.
    """

    # TODO: Need to add invent and handler for rejecting attacks!!!

    name = models.CharField(_('Name'), max_length=100)
    phone_number = models.CharField(_('Phone Number'), max_length=50)
    email = models.EmailField(_('Email address'), max_length=255)
    is_answered = models.BooleanField(_('Is answered'), default=False)


class ContactUsRequest(UUIDAbstractModel, TimeStampedModel):
    """
    Model for saving messages from `ContactUsForm` in the database.
    """
    message = models.TextField(_('Message'), max_length=5000)
    name = models.CharField(_('Name'), max_length=255)
    email = models.EmailField(_('Email address'), max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='contact_us_messages',
        verbose_name=_('User'), null=True, blank=True,
        on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.email

    def get_admin_url(self):
        return '{protocol}://{domain}{path}'.format(
            protocol=get_protocol(),
            domain=Site.objects.get_current().domain,
            path=reverse('admin:common_contactusrequest_change', args=[self.id]))


class CategorySection(models.Model):
    category = models.ForeignKey(
        'catalogue.Category',
        verbose_name=_("Categories"), related_name='sections')
    position = models.PositiveSmallIntegerField(_('Position in list'), default=0)
    slug = models.SlugField(_('Slug'), max_length=255)
    title = models.CharField(_('Title'), max_length=255)
    icon = models.ImageField(
        _('Icon'), upload_to='uploads/category_section/', blank=True, null=True)
    image = models.ImageField(
        _('Image'), upload_to='uploads/category_section/', blank=True, null=True)
    content = RichTextField(_('Content'))

    class Meta:
        ordering = ('position', '-title')

    def generate_slug(self):
        return slugify(self.title)

    def save(self, *args, **kwargs):
        if self.slug:
            super().save(*args, **kwargs)
        else:
            self.slug = self.generate_slug()
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'catalogue:category',
            kwargs={
                'category_slug': self.category.full_slug,
                'pk': self.pk
            }
        ) + '#section-%s' % self.id


class DosimeterPDFReportTheme(UUIDAbstractModel):

    body = models.TextField(_('Body'))
    min_concentration = models.PositiveSmallIntegerField(
        _('Minimal Concentration'), default=0)
    max_concentration = models.PositiveSmallIntegerField(
        _('Maximal Concentration'), default=0)
    owner = models.ForeignKey(
        'owners.Owner', verbose_name=_('Owner'),
        null=True, blank=True, related_name='dosimeter_pdf_themes')

    class Meta:
        ordering = ('min_concentration',)

    def __str__(self):
        return 'MIN: %s | MAX: %s' % (self.min_concentration, self.max_concentration)

    @classmethod
    def get_theme(cls, order):
        """
        Get theme according to avg_concentration
        """
        avg_concentration = order.dosimeters_avg_concentration
        if not order.owner_id or not avg_concentration:
            return

        # Never mix text between owners
        # So select if all conditions are fitted.
        theme = cls.objects.filter(
            owner_id=order.owner_id,
            min_concentration__lte=avg_concentration,
            max_concentration__gte=avg_concentration).first()
        return theme
