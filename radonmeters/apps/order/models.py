# -*- coding: utf-8 -*-
from constance import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q, F
from django.template.loader import get_template
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from oscar.apps.address.abstract_models import AbstractShippingAddress
from oscar.apps.order.abstract_models import AbstractOrder
from oscar.core.loading import get_model
from weasyprint import HTML
from django.template import engines, VariableDoesNotExist

from common.models import DosimeterPDFReportTheme
from common.validators import PhoneNumberValidator

import numpy as np

from customer.utils import get_email_templates

from customer.utils import COMM_TYPE_DOSIMETERS_REGISTERED

ORDER_NOT_FULL = 10
ORDER_IS_WEIRD = 20
ORDER_NO_DOSIMETERS = 30

class OrderedDosimetersMixin:
    """
    Mixin for providing methods for working with data of ordered dosimeters.
    """

    _why_not_approved = None

    @cached_property
    def dosimeters_line(self):
        """
        Returns the first line with dosimeters in the order.
        """

        return self.lines.filter(dosimeters__isnull=False).first()

    def get_measurement_date_min(self):
        from catalogue.models import Dosimeter

        d = Dosimeter.objects.filter(
            line__order=self,
            measurement_start_date__isnull=False
        ).order_by('measurement_start_date').first()

        if d:
            return d.measurement_start_date

    def get_measurement_date_max(self):
        from catalogue.models import Dosimeter

        d = Dosimeter.objects.filter(
            line__order=self,
            measurement_end_date__isnull=False
        ).order_by('measurement_end_date').last()

        if d:
            return d.measurement_end_date

    @property
    def dosimeters_pdf_report_can_be_generated(self):
        """
        Checks that PDF report for dosimeters can be generated.

        :return: Boolean value.
        """

        # TODO: Need to optimize it (to many requests to db).

        Dosimeter = get_model('catalogue', 'Dosimeter')

        # Get number of active dosimeters in the order.
        num_of_dosimeters = Dosimeter.objects.filter(
            is_active=True,
            line__order_id=self.pk).count()

        # If the order doesn't have the dosimeters,
        # return false immediately.
        if num_of_dosimeters < 1:
            self._why_not_approved = ORDER_NO_DOSIMETERS
            return False

        # Get number of dosimeters prepared for generating in PDF report.
        num_of_dosimeters_with_results = Dosimeter.objects.filter(
            # All fields below should be filled.
            ~Q(location__exact='') & ~Q(concentration=0.0),
            # Filter dosimeters by line > order.
            line__order_id=self.pk,
            is_active=True,

            # All fields below should be filled.
            # Data from them, needed for generating PDF report.
            concentration__isnull=False,
            uncertainty__isnull=False,
            measurement_start_date__isnull=False,
            measurement_end_date__isnull=False,
            floor__isnull=False,
        ).count()

        # Compare numbers.
        if num_of_dosimeters_with_results != num_of_dosimeters:
            self._why_not_approved = ORDER_NOT_FULL
            return False

        # Check that order is not weird
        if self.not_weird:
            return True
        if self.is_weird_outlier or self.is_weird_overlap_1 or self.is_weird_overlap_2:
            self._why_not_approved = ORDER_IS_WEIRD
            return False
        return True

    @property
    def dosimeters_pdf_report_non_approval_reason(self):
        """
        Returns the reason why pdf report cannot be generated.

        :return: integer value (from a list of enumerated constants).
        """

        if self._why_not_approved is not None:
            return self._why_not_approved
        else:
            self.dosimeters_pdf_report_can_be_generated # recalculate
            return self._why_not_approved

    @cached_property
    def dosimeters_avg_concentration(self):
        """
        Returns average concentration based on dosimeters results.

        :return: Flat number (rounded).
        """

        # Make next actions only if all needed data is exists.
        if self.dosimeters_pdf_report_can_be_generated:
            # use previous calculation
            return self.dosimeters_line.dosimeters.first().avg_concentration_visual
            # dosimeters = self.dosimeters_line.dosimeters.all()
            # concentration_sum = sum([d.concentration_visual or 0 for d in dosimeters])
            # return round(concentration_sum / len(dosimeters), 2)

    def dosimeters_pdf_report_generate(self, logo=None, template=None, as_image=False):
        """
        Generate Dosimeters PDF report for customer.

        :return: The PDF as byte string.
        """

        # Check that report can be generated.
        if self.use_external_report and self.external_report_pdf:
            return self.external_report_pdf.read()
        if self.dosimeters_pdf_report_can_be_generated:
            theme = DosimeterPDFReportTheme.get_theme(self)
            body = theme.body if theme else ''

            if not template:
                logo, template = Order.get_dosimeters_pdf_report_data(self)
            else:
                django_engine = engines['django']
                template = django_engine.from_string(template)
                logo = logo or config.DOSIMETERS_REPORT_LOGO

            # Prepare html for rendering to PDF.
            context = {
                'user': self.user,
                'order': self,
                "line": self.dosimeters_line,
                "logo": logo,
                "dosimeter_description": body}

            try:
                html = template.render(context)
            except VariableDoesNotExist:
                return _('Error during report rendering.')

            # Generate and return report file.
            html = HTML(
                string=html,
                encoding='UTF-8',
                base_url=settings.MEDIA_ROOT
            )
            if as_image:
                return html.write_png()
            return html.write_pdf()

    @staticmethod
    def get_dosimeters_pdf_report_data(order):
        if order.owner and hasattr(order.owner, 'report_template'):
            template_obj = order.owner.report_template
            logo = template_obj.logo or config.DOSIMETERS_REPORT_LOGO
            django_engine = engines['django']
            template = django_engine.from_string(template_obj.pdf_template)
        else:
            logo = config.DOSIMETERS_REPORT_LOGO
            template = get_template('pdf/dosimeters_report.html')
        return logo, template


class Order(
        OrderedDosimetersMixin,
        AbstractOrder):
    """
    Overridden for providing custom logic and store for custom data.
    """

    shipping_id = models.CharField(
        verbose_name=_('Shipping ID'),
        help_text=_('Code for checking where is order now.'),
        blank=True,
        max_length=255)
    shipping_return_id = models.CharField(
        verbose_name=_('Shipment ID for Return Label'),
        help_text=_('Code for return label.'),
        blank=True,
        max_length=255)
    partner_order_id = models.CharField(
        verbose_name=_('Partner order ID'),
        help_text=_('ID of order in the partner\'s system.'),
        blank=True,
        max_length=255)
    is_approved = models.BooleanField(
        verbose_name=_('Is approved'),
        default=False)
    user_who_approved = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User who approved the order.'),
        blank=True, null=True)
    approved_date = models.DateTimeField(
        _('Approved date'),
        blank=True, null=True)
    owner = models.ForeignKey(
        'owners.Owner',
        verbose_name=_('Owner'), blank=True, null=True)
    is_reported_by_partner = models.BooleanField(
        _('Reported by partner?'), default=False)
    is_report_sent = models.BooleanField(
        verbose_name=_('Is report sent?'),
        default=False)
    use_external_report = models.BooleanField(
        verbose_name=_('Use external report?'),
        default=False)
    external_report_pdf = models.FileField(
        _('External report'),
        upload_to='reports/external/',
        blank=True)
    sent_date = models.DateTimeField(
        _('Sent date'),
        blank=True, null=True)
    is_weird_outlier = models.BooleanField(
        _('Suspect result - outlier concentration'), default=False)
    is_weird_overlap_1 = models.BooleanField(
        _('Suspect result - Level 1 concentration overlap'), default=False)
    is_weird_overlap_2 = models.BooleanField(
        _('Suspect result - Level 2 concentration overlap'), default=False)
    not_weird = models.BooleanField(
        _('Results are correct even though suspect?'), default=False)
    not_weird_explanation = models.CharField(
        _('Why results are correct even though suspect'), max_length=255, blank=True)

    # payment data
    is_exists_accounting = models.BooleanField(
        _('Is exist'),
        help_text=_('Show if an order has been registered in accounting system'),
        default=False)
    is_paid = models.BooleanField(
        _('Is paid'), default=False)
    date_payment = models.DateTimeField(
        _('Date of payment'), blank=True, null=True)

    def get_total_weight(self):
        """
        Calculates and returns total weight, based on weight of each product.
        """
        return sum(l.product.weight * l.quantity for l in self.lines.all())

    def available_statuses(self):
        """
        Returns all possible statuses that this order can move to.
        """

        # Prepare list of available statuses (Oscar's default realisation).
        available_statuses = self.pipeline.get(self.status, ())

        # If status `issued` in `available_statuses`, and not all product items
        # which included in current order have serial number,
        # exclude `issued` from list of available statuses.
        if 'issued' in available_statuses and self.lines.filter(
                Q(products__serial_number='')
                | Q(dosimeters__serial_number='')).exists():
            return [s for s in available_statuses if s != 'issued']

        # Else, return default list.
        return available_statuses

    def prepare_pdf_report_response(self, logo=None, template=None):
        from django.http import HttpResponse
        if self.dosimeters_pdf_report_can_be_generated:
            # Prepare data.
            file_data = self.dosimeters_pdf_report_generate(logo, template, True)
            file_name = 'Report for order #%s.pdf' % self.number

            # Prepare response.
            # response = HttpResponse(content_type='application/pdf')
            response = HttpResponse(content_type='image/png')
            # Load pdf
            # response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            # View on the current page
            response['Content-Disposition'] = 'inline;'
            response.write(file_data)
            return response

    def get_from_email(self):
        return self.owner.get_from_email() if self.owner_id else settings.DEFAULT_FROM_EMAIL

    def get_user_name(self):
        return self.user.get_full_name() if self.user else self.email

    def get_connection(self):
        return self.owner.get_connection() if self.owner_id else None

    def update_status(self):
        """Change status from 'created' to 'issued' if all dosimeters have serial numbers.
        """
        if (self.status == 'created' and
            'issued' in self.available_statuses()):
            self.status = 'issued'

    def update_weirdness_statuses(self):
        """Recalculate if order is looking weird by checking values of it's dosimiters.

        3 metrics are used:
         * outlier metric -- for dosimeters with concentration which is far out
         * level 1 overlap -- if dosimeter on upper floor has greater value than on lower floor (with 1x uncertainty)
         * level 2 overlap -- if dosimeter on upper floor has greater value than on lower floor (with 2x uncertainty)
        """
        self.is_weird_outlier = False
        self.is_weird_overlap_1 = False
        self.is_weird_overlap_2 = False
        # constants
        k = 1.5 # for outlier calculation when number of dosimeters > 2
        outlier_threshold = 50 # for outlier calculation
        # Now calculate if an order is weird
        concentrations = []
        uncertainties = []
        floors = []
        for line in self.lines.all():
            for dosimeter in line.dosimeters.order_by('floor'):
                if dosimeter.concentration_visual is None:
                    continue
                concentrations.append(dosimeter.concentration_visual)
                if dosimeter.uncertainty_visual is not None:
                    uncertainties.append(dosimeter.uncertainty_visual)
                else:
                    uncertainties.append(0)
                floors.append(dosimeter.floor)
        for i in range(len(concentrations)):
            c_1 = concentrations[i]
            u_1 = uncertainties[i]
            for j in range(i):
                c_2 = concentrations[j]
                u_2 = uncertainties[j]
                if floors[i] is not None and floors[j] is not None:
                    if floors[i] <= floors[j]:
                        if c_1 + u_1 - c_2 + u_2 < 0:
                            self.is_weird_overlap_1 = True
                        if c_1 + 2*u_1 - c_2 + 2*u_2 < 0:
                            self.is_weird_overlap_2 = True
                    else:
                        if c_2 + u_2 - c_1 + u_1 < 0:
                            self.is_weird_overlap_1 = True
                        if c_2 + 2*u_2 - c_1 + 2*u_1 < 0:
                            self.is_weird_overlap_2 = True
        if len(concentrations) == 2:
            if abs(c_1-c_2)-2*(u_1+u_2) > outlier_threshold:
                self.is_weird_outlier = True
        elif len(concentrations) > 2:
            quartiles = np.percentile(concentrations, [25, 75])
            q_1 = quartiles[0]
            q_3 = quartiles[1]
            uncertainties = [u for u, c in sorted(zip(uncertainties, concentrations), key=lambda pair: pair[1])]
            concentrations = sorted(concentrations)
            for i in range(len(concentrations)):
                c_1 = concentrations[i]
                # https://en.wikipedia.org/wiki/Outlier#Tukey's_fences
                if c_1 < q_1 - k*(q_3-q_1) or c_1 > q_3 + k*(q_3-q_1):
                    u_1 = uncertainties[i]
                    if i != 0:
                        c_left = concentrations[i-1]
                    else:
                        c_left = float('-inf')
                    if i != len(concentrations)-1:
                        c_right = concentrations[i+1]
                    else:
                        c_right = float('+inf')
                    if abs(concentrations[i]-c_left) < abs(concentrations[i]-c_right):
                        c_2 = concentrations[i-1]
                        u_2 = uncertainties[i-1]
                    else:
                        c_2 = concentrations[i+1]
                        u_2 = uncertainties[i+1]
                    if abs(c_1-c_2)-2*(u_1+u_2) > outlier_threshold:
                        self.is_weird_outlier = True

    def scan_dosimeters(self):
        """Check all dosimeters and send e-mail if all dosimeters have status `on_store_side`.

        Return True if e-mail was sent, and False otherwise.
        """
        are_all_registered = True
        counter = 0
        for line in self.lines.all():
            for dosimeter in line.dosimeters.filter(is_active=True):
                counter += 1
                if dosimeter.status != 'on_store_side':
                    return False
        if counter == 0:
            return False
        if are_all_registered:
            msg = self.prepare_email_msg(COMM_TYPE_DOSIMETERS_REGISTERED)
            msg.send()
        return are_all_registered

    def prepare_email_msg(self, comm_type, context=None):
        context = context or {}
        context['order'] = self
        context['user'] = self.user
        email_templates = get_email_templates(comm_type=comm_type, context=context)
        subject = email_templates.get('subject')
        message = email_templates.get('message')
        html_message = email_templates.get('html_message')

        from_email = self.get_from_email()
        msg = EmailMultiAlternatives(
            subject, message, from_email, [self.email],
            connection=self.get_connection())
        msg.attach_alternative(html_message, "text/html")
        return msg

    def send_email_with_pdf(self, comm_type, filename, file_content, context=None):
        msg = self.prepare_email_msg(comm_type, context)
        msg.attach(
            filename=filename,
            content=file_content,
            mimetype="application/pdf")

        # catch exception
        msg.send()


class ShippingAddress(AbstractShippingAddress):
    """
    Overridden for replacing field `phone_number` with custom realisation.
    """

    phone_number = models.CharField(
        _('Phone Number'),
        help_text=_('Phone number in the international format.'),
        max_length=15, validators=[PhoneNumberValidator()], blank=True)

    def get_address(self):
        """
        Combines lines and return it as string with address.
        """

        address = " ".join([self.line1, self.line2, self.line3])
        return address.strip()

    def get_city(self):
        """
        Tries to find and return city name (or blank string).
        """

        if self.line4:
            return self.line4
        elif self.state:
            return self.state
        else:
            return ''

# Order filters
def filter_approved():
    """
    Approved.
    """
    filter = Q(is_approved=True)
    return filter

def filter_ready_for_approval():
    filter = filter_no_result()
    filter |= filter_no_slip()
    return ~filter

def filter_ready_for_approval_but_not_approved():
    """
    Ready for approval, but not approved.
    """
    filter = filter_ready_for_approval()
    filter &= Q(is_approved=False)
    return filter

def filter_not_ready_for_approval_and_not_approved():
    """
    Not ready for approval and not approved.
    """
    filter = ~filter_ready_for_approval()
    filter &= Q(is_approved=False)
    return filter

def filter_sent_or_reported():
    """
    Sent or reported.
    """
    filter = Q(is_reported_by_partner=True) | Q(is_report_sent=True)
    return filter

def filter_no_lab():
    """
    At least one lab is missing.
    """
    Dosimeter = get_model('catalogue', 'Dosimeter')
    filter_no_lab = (Q(concentration__isnull=True) | Q(concentration=0.0))
    dosimeters_no_lab = Dosimeter.objects.active().filter(filter_no_lab)
    filter = Q(lines__dosimeters__in=(dosimeters_no_lab))
    return filter

def filter_no_result():
    """
    At least one result is missing.
    """
    Dosimeter = get_model('catalogue', 'Dosimeter')
    filter_no_result = ((Q(concentration__isnull=True) | Q(concentration=0.0)) |
                        Q(uncertainty__isnull=True))
    dosimeters_no_result = Dosimeter.objects.active().filter(filter_no_result)
    filter = Q(lines__dosimeters__in=(dosimeters_no_result))
    return filter

def filter_no_slip():
    """
    At least one slip is missing.
    """
    Dosimeter = get_model('catalogue', 'Dosimeter')
    filter_no_slip = (Q(measurement_start_date__isnull=True) |
              Q(measurement_end_date__isnull=True) |
              (Q(location__isnull=True) | Q(location__exact='')) |
              Q(floor__isnull=True))
    dosimeters_no_slip = Dosimeter.objects.active().filter(filter_no_slip)
    filter = Q(lines__dosimeters__in=(dosimeters_no_slip))
    return filter

def filter_no_slip_or_no_result():
    """
    At least one lab or one slip is missing.
    """
    filter = filter_no_result()
    filter |= filter_no_slip()
    return filter

def filter_empty():
    """
    Orders with no data for dosimeters.
    """
    Dosimeter = get_model('catalogue', 'Dosimeter')
    filter_nonempty = (Q(measurement_start_date__isnull=False) |
         Q(measurement_end_date__isnull=False) |
         ~Q(location__exact='') |
         Q(floor__isnull=False) |
         (Q(concentration__isnull=False) & ~Q(concentration=0.0)) |
         Q(uncertainty__isnull=False))
    nonempty_dosimeters = Dosimeter.objects.active().filter(filter_nonempty)
    filter = Q(lines__dosimeters__in=(nonempty_dosimeters))
    return ~filter

def filter_slip_no_result():
    """
    All slips are inserted, but at least one result is missing AND order is not ready for aprroval.
    """
    filter = ~filter_no_slip()
    filter &= filter_no_result()
    filter &= ~filter_ready_for_approval()
    return filter

def filter_result_no_slip():
    """
    All results are inserted, but at least one slip is missing AND order is not ready for aprroval.
    """
    filter = ~filter_no_result()
    filter &= filter_no_slip()
    filter &= ~filter_ready_for_approval()
    return filter

def filter_partial():
    """
    Nonfinished orders that are not in the following categories:
     * filter_empty
     * filter_ready_for_approval
     * filter_slip_no_result
     * filter_result_no_slip
    """
    filter = filter_no_slip_or_no_result()
    filter &= ~(filter_ready_for_approval() | filter_slip_no_result() | filter_result_no_slip() | filter_empty())
    return filter

# noinspection PyUnresolvedReferences
from oscar.apps.order.models import *
