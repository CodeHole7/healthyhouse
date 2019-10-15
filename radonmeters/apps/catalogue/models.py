# -*- coding: utf-8 -*-
import pandas as pd
from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from oscar.apps.catalogue.abstract_models import AbstractCategory
from oscar.apps.catalogue.abstract_models import AbstractProduct
from oscar.apps.partner.models import StockRecord
from oscar.core.loading import get_model
from rest_framework.reverse import reverse
from django.utils import timezone

from common.models import UUIDAbstractModel


"""
    @author: alex m
    @created: 2019.8.29
"""
from django.template.loader import get_template
import qrcode
import qrcode.image.svg
from pylibdmtx.pylibdmtx import encode
from PIL import Image
import os
from weasyprint import HTML
import base64
import io

from owners.models import Owner


Line = get_model('order', 'Line')


class Category(AbstractCategory):
    """
    Overridden for adding custom fields and logic for categories.
    """

    description = RichTextField(_('Description'), blank=True)


class Product(AbstractProduct):
    """
    Overridden for adding custom fields and logic for products.
    """

    lead = models.TextField(
        verbose_name=_('Lead'),
        help_text=_('Lead paragraph'),
        max_length=450,
        blank=True)
    description = RichTextField(
        verbose_name=_('Description'),
        blank=True)
    specification = RichTextField(
        verbose_name=_('Specification'),
        blank=True)
    youtube_video_id = models.CharField(
        max_length=255,
        help_text=_('Example: Hg9MMVBHPAk)'),
        blank=True)
    weight = models.PositiveIntegerField(
        verbose_name=_('Weight'),
        help_text=_('Weight of product in grams.'),
        blank=True,
        null=True)
    min_num_for_order = models.PositiveSmallIntegerField(
        verbose_name=_('Minimal number for order.'),
        default=1)
    product_usage = RichTextField(
        verbose_name=_('Product usage'),
        help_text=_('Usage instructions. (Dosimeters Only)'),
        blank=True)

    @property
    def first_category(self):
        return self.get_categories().first()

    @property
    def total_net_stock_level(self):
        """
        Implements default `AbstractStockRecord.net_stock_level`
        for all partners by one request (per product).
        :return:
        """
        counts = StockRecord.objects.filter(product=self).aggregate(
            _num_in_stock=Coalesce(Sum('num_in_stock'), 0),
            _num_allocated=Coalesce(Sum('num_allocated'), 0))
        return max(counts['_num_in_stock'] - counts['_num_allocated'], 0)


class ProductItemAbstractModel(UUIDAbstractModel, TimeStampedModel):
    """
    Model for storing data of each product in the each order.

    Has relation with customer through: `line > order > user`.
    """

    serial_number = models.CharField(
        _('Serial number'), max_length=50, blank=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-line__order__date_placed', '-created')

    def __str__(self):
        return self.line.product.get_title()

    def get_serial_number(self):
        """
        Represents `serial_number`.
        """
        return self.serial_number or None

    def clean(self):

        # Check that `serial_number` is unique if it's exists.
        if self.serial_number:
            is_not_unique = self._meta.model.objects.exclude(
                id=self.pk
            ).filter(
                serial_number=self.serial_number
            ).exists()

            if is_not_unique:
                message = _('This serial number already exists in the database.')
                raise ValidationError({'serial_number': message})


class DefaultProduct(ProductItemAbstractModel):
    """
    Model for storing data of each ordered product with
    `product_class.name = "Default"`
    """

    line = models.ForeignKey(
        Line, related_name='products', verbose_name=_('Line'))


class DosimeterQueryset(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class Dosimeter(ProductItemAbstractModel):
    """
    Model for storing data of each ordered product with
    `product_class.name = "Dosimeter"`
    """

    """
    -1 = basement,
    0 = living room,
    1 = 1st floor,
    2 = 2nd floor
    3 = 3rd floor or higher.
    """

    FLOOR_CHOICES = Choices(
        (-1, 'basement', _('Basement')),
        (0, 'living_room', _('Living room')),
        (1, '1st_floor', _('1st floor')),
        (2, '2nd_floor', _('2nd floor')),
        (3, '3rd_floor_or_higher', _('3rd floor or higher')))

    STATUS_CHOICES = Choices(
        ('unknown', 'unknown', _('Unknown')),
        ('created', 'created', _('Created')),

        ('ready_for_packaging', 'ready_for_packaging', _('Ready_for_packaging')),
        ('shipped_to_distributor', 'shipped_to_distributor', _('Shipped_to_distributor')),
        ('recieved_from_distributor', 'recieved_from_distributor', _('Recieved_from_distributor')),
        ('on_client_side', 'on_client_side', _('On client side')),
        ('on_store_side', 'on_store_side', _('On store side')),
        ('on_lab_side', 'on_lab_side', _('On lab side')),
        ('completed', 'completed', _('Completed')))

    status = models.CharField(
        _('Status'), max_length=30, choices=STATUS_CHOICES,
        default=STATUS_CHOICES.unknown)

    line = models.ForeignKey(
        Line, related_name='dosimeters', verbose_name=_('Line'), blank=True, null=True)

    # Data which should be set by 3rd-party application:
    concentration = models.FloatField(_('Concentration'), null=True, blank=True)
    uncertainty = models.FloatField(_('Uncertainty'), null=True, blank=True)

    # Data which should be set by customer:
    measurement_start_date = models.DateField(
        _('Measurement start date'), null=True, blank=True)
    measurement_end_date = models.DateField(
        _('Measurement end date'), null=True, blank=True)
    floor = models.SmallIntegerField(
        _('Floor'), choices=FLOOR_CHOICES, null=True, blank=True)
    location = models.CharField(_('Location'), max_length=255, blank=True)
    active_area = models.BooleanField(
        _('Active Area'), default=True)
    use_raw_concentration = models.BooleanField(
        _('Should we use raw concentration and uncertainty?'), default=False)
    is_active = models.BooleanField(
        _('Is active?'), default=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        verbose_name=_('User who made the last modification of the dosimeter'),
        blank=True, null=True)
    last_modified_date = models.DateField(
        _('Date of last edition'), null=True, blank=True)

    # New fields only accessible from database
    service_price = models.FloatField(_('Service price'), null=True, blank=True)
    is_invoiced = models.BooleanField(_('Is invoiced?'), default=True)

    objects = DosimeterQueryset.as_manager()

    def clean(self):
        super().clean()

        # Check that `start_date` less or equal with `end_date`.
        start_date = self.measurement_start_date
        end_date = self.measurement_end_date
        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                _('Start date cannot be greater than the end date.'))

        # TODO: Need to add validation for diff between these dates (min 7).

    def get_absolute_url(self):
        return reverse('api:profile:dosimeter_details', kwargs={'pk': self.pk})

    def get_status_as_dict(self):
        """
        Represents status field as dictionary with title and value.
        """
        return {
            'title': self.get_status_display(),
            'value': self.status}

    def pdf_report_can_be_generated(self):
        """
        Checks that all dosimeters of this line have results from laboratory.
        """
        dosimeters_with_results = self.line.dosimeters.filter(
            concentration__isnull=False,
            uncertainty__isnull=False).count()
        return dosimeters_with_results == self.line.quantity

    @cached_property
    def measurement_days(self):
        """
        Returns delta between measurement's start and end dates (in days).
        """
        if all([self.measurement_start_date, self.measurement_end_date]) \
                and self.measurement_start_date <= self.measurement_end_date:
            diff = self.measurement_end_date - self.measurement_start_date
            return max([7, diff.days])

    @cached_property
    def measurement_hours(self):
        """
        Returns delta between measurement's start and end dates (in hours).
        """
        if self.measurement_days:
            return self.measurement_days * 24

    """
        @author: alex m
        @created: 20198.30
        @desc: get owner of dosimeter if it be assinged
    """
    @cached_property
    def get_owner_name(self):
        
        if self.status is not self.STATUS_CHOICES.unknown and self.status is not self.STATUS_CHOICES.created:
            try:

                batch_dosimeter = Batch_Dosimeter.objects.get(dosimeter_id = self.id)
                batch = batch_dosimeter.batch
                owner = batch.batch_owner

                return owner.first_name
            except Batch_Dosimeter.DoesNotExist:
                pass
        return False
    @cached_property
    def get_batch_description(self):
        
        if self.status is not self.STATUS_CHOICES.unknown and self.status is not self.STATUS_CHOICES.created:
            try:

                batch_dosimeter = Batch_Dosimeter.objects.get(dosimeter_id = self.id)
                batch = batch_dosimeter.batch

                return batch.batch_description
            except Batch_Dosimeter.DoesNotExist:
                pass
        return False

    @property
    def concentration_visual(self):
        """
        Calculates and returns `concentration` for showing to end user.
        Or if use_raw_concentration=True retun own concentration
        """
        if self.use_raw_concentration:
            return self.concentration

        if self.measurement_hours and self.concentration:
            return round(1000 * (self.concentration / self.measurement_hours), 2)

    @property
    def uncertainty_visual(self):
        """
        Calculates and returns `uncertainty` for showing to end user.
        Or if use_raw_concentration=True retun own uncertainty
        """
        if self.use_raw_concentration:
            return self.uncertainty
        if self.measurement_hours and self.uncertainty:
            return round(1000 * (self.uncertainty / self.measurement_hours), 2)

    @property
    def avg_concentration_visual(self):
        """
        Returns average concentration based on dosimeters results.
        When the yearly average is calculated we need to do the following.
        multiply all visual concentrations with active_area,
        then group dosimeters by the variable 'floor'
        and calculate average for each floor.
        When all average has been calculated, the average of the averages should be calculated.

        Example:
        import pandas as pd
        dosimeters = pd.DataFrame([[0,-1,117],[1,-1,113],[1,0,135],[0,0,138],[1,0,210],[1,1,213],[1,1,73]],columns = ['active_area','floor','conc_visual'])
        mus = dosimeters.groupby('floor').apply(lambda x : 0 if x['active_area'].sum() == 0 else (x['active_area']*x['conc_visual']).sum()/x['active_area'].sum()).sum()
        div = dosimeters.groupby('floor').apply(lambda x : x['active_area'].sum() != 0).sum()
        yearly_avg = mus/div

        :return: Flat number (rounded).
        """
        # TODO Optimize qs without filter
        dosimeters = self.line.dosimeters.filter(is_active=True)
        # dosimeters = self.line.dosimeters.all()
        if not dosimeters:
            return

        data_dosimeters = [[
            d.active_area,
            d.floor,
            d.concentration_visual]
            for d in dosimeters if d.is_active]
        if not all(array_obj[2] is not None for array_obj in data_dosimeters):
            # check if all dosimeters can calculate conc_visual
            return
        if not all(array_obj[1] is not None for array_obj in data_dosimeters):
            # check if all dosimeters has a floor
            return

        dosimeters = pd.DataFrame(data_dosimeters, columns=['active_area', 'floor', 'conc_visual'])
        mus = dosimeters.groupby('floor').apply(
            lambda x: 0 if x['active_area'].sum() == 0 else (x['active_area'] * x['conc_visual']).sum() / x[
                'active_area'].sum()).sum()
        div = dosimeters.groupby('floor').apply(lambda x: x['active_area'].sum() != 0).sum()
        if div:
            yearly_avg = mus / div
        else:
            yearly_avg = 0
        return round(yearly_avg, 2)

    @classmethod
    def qs_for_lines(cls, lines):
        dosimeter_slug = settings.OSCAR_PRODUCT_TYPE_DOSIMETER.lower()
        lines_with_dosimeter_products = [
            l for l in lines.all() if l.product.product_class.slug == dosimeter_slug]

        return cls.objects.filter(
            line__in=lines_with_dosimeter_products)

    """
        @author: alex m
        @created: 2019.8.29
        @desc: generate report for datamatrix
    """
    def dosimeter_pdf_report_generate(self, logo=None, template=None, as_image=False):
        """
        Generate Dosimeters PDF report for customer.

        :return: The PDF as byte string.
        """

        # Check that report can be generated.
        pdf_url = "dosimeter_pdf/%s.pdf"%self.serial_number
        abs_url =os.path.join('./radonmeters/static',  pdf_url) 
            
        if(os.path.exists(abs_url) == False):
            template = get_template('pdf/dosimeter_report.html')
            logo = ''

            datamatrixs = self.generated_datamatrix()
            # Prepare html for rendering to PDF.
            context = {
                "logo": logo,
                "serial_number": str(self.serial_number)[1:],
                "datamatrix1":datamatrixs[0],
                "datamatrix2":datamatrixs[1]
            }

            try:
                html = template.render(context)
            except VariableDoesNotExist:
                return None

            # Generate and return report file.
            html = HTML(
                string=html,
                encoding='UTF-8',
            )
            if as_image:
                return html.write_png()
            html.write_pdf(abs_url)
        return abs_url
    """
        @author: alex m
        @created: 2019.8.29
        @desc: get qr code
    """
    def generated_datamatrix(self):
        if self.serial_number is not None:
            
            # change prefix 0 -> 1
            ser = self.serial_number[1:]
            ser_1 = "1" + str(ser)
            ser_2 = "2" + str(ser)

            # datamatrix with prefix 1
            

            img_buffer = io.BytesIO()
            
            encoded = encode(ser_1)
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
            img.save(img_buffer,format="PNG")


            base64Img1 = base64.b64encode(img_buffer.getvalue())

            # datamatrix with prefix 2


            encoded = encode(ser_2)
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
            img.save(img_buffer,format="PNG")

            base64Img2 = base64.b64encode(img_buffer.getvalue())

            return base64Img1, base64Img2

class Location(TimeStampedModel):
    name = models.CharField(_('Location'), max_length=255, unique=True)
    # add language

    class Meta:
        ordering = ('name', '-created')

    def __str__(self):
        return self.name

"""
    @author: alex m
    @created: 2019.8.29
    @desc: Batch table model for dosimeter grouping
"""
class Batch(models.Model):
    batch_description = models.CharField(_('Batch Description'), max_length=512, blank=True)
    batch_owner = models.ForeignKey(Owner)
    created_date = models.DateTimeField( _('Date of creation'),auto_now_add=True)
    # created_date = models.DateField(
    #     _('Date of creation'), null=True, default=timezone.now())
    
"""
    @author: alex m
    @created: 2019.8.29
    @desc: Batch_Dosimeter table model for dosimeter grouping
"""
class Batch_Dosimeter(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    dosimeter = models.ForeignKey(Dosimeter, on_delete=models.CASCADE)
    
class DosimeterNote(models.Model):
    note_type = models.CharField(max_length=255)
    message = models.TextField(null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    dosimeter = models.ForeignKey(Dosimeter, on_delete = models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        blank=True, null=True)

# noinspection PyUnresolvedReferences
from oscar.apps.catalogue.models import *
