import datetime
from django.conf import settings
from django.db.models import F, Q, OuterRef, Exists
from django.views.generic import ListView, TemplateView
from django.utils.translation import gettext_lazy as _
from oscar.apps.dashboard.orders.views import \
    LineDetailView as CoreLineDetailView
from oscar.apps.dashboard.orders.views import OrderListView as OrderListViewBase
from oscar.core.loading import get_model
from oscar.core.utils import datetime_combine
from oscar.views import sort_queryset

from catalogue.models import Dosimeter
from common.utils import is_radosure

from order.models import filter_ready_for_approval_but_not_approved, \
    filter_approved, \
    filter_sent_or_reported, \
    filter_not_ready_for_approval_and_not_approved, \
    filter_empty, \
    filter_partial, \
    filter_result_no_slip, \
    filter_slip_no_result

from dashboard.orders.forms import APPROVAL_STATUS_CHOICES
from dashboard.orders.forms import REPORT_STATUS_CHOICES
from dashboard.orders.forms import ANALYSIS_STATUS_CHOICES
from dashboard.orders.forms import WEIRDNESS_STATUS_CHOICES
from dashboard.orders.forms import ORDER_STATUS_CHOICES
from dashboard.orders.forms import SHIPMENT_STATUS_CHOICES
APPROVAL_STATUS_CHOICES_DICT = dict(APPROVAL_STATUS_CHOICES)
REPORT_STATUS_CHOICES_DICT = dict(REPORT_STATUS_CHOICES)
ANALYSIS_STATUS_CHOICES_DICT = dict(ANALYSIS_STATUS_CHOICES)
WEIRDNESS_STATUS_CHOICES_DICT = dict(WEIRDNESS_STATUS_CHOICES)
ORDER_STATUS_CHOICES_DICT = dict(ORDER_STATUS_CHOICES)
SHIPMENT_STATUS_CHOICES_DICT = dict(SHIPMENT_STATUS_CHOICES)

Line = get_model('order', 'Line')
Owner = get_model('owners', 'Owner')
Partner = get_model('partner', 'Partner')
Product = get_model('catalogue', 'Product')
Country = get_model('address', 'Country')


class LineDetailView(CoreLineDetailView):
    """
    Overridden for providing custom context and templates.
    """

    model = Dosimeter

    def get_template_names(self):
        if self.object.product.product_class.name == settings.OSCAR_PRODUCT_TYPE_DEFAULT:
            return ['dashboard/orders/line_detail_for_default_products.html']
        elif self.object.product.product_class.name == settings.OSCAR_PRODUCT_TYPE_DOSIMETER:
            return ['dashboard/orders/line_detail_for_dosimeters.html']
        else:
            return ['dashboard/orders/line_detail.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.product.product_class.name == settings.OSCAR_PRODUCT_TYPE_DEFAULT:
            context['default_products'] = self.object.products.all()
        elif self.object.product.product_class.name == settings.OSCAR_PRODUCT_TYPE_DOSIMETER:
            context['dosimeters'] = self.object.dosimeters.all()

        return context


class OrderListView(OrderListViewBase):

    def get_template_names(self):
        if is_radosure():
            return ['radosure_dashboard/orders/order_list.html']
        return super().get_template_names()

    def get(self, request, *args, **kwargs):
        """
        Prevent redirect to detail page after search on order list.
        """
        return super(ListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Build the queryset for this list.
        """

        # Default oscar filtering
        # -----------------------
        queryset = sort_queryset(self.base_queryset, self.request,
                                 ['number', 'total_incl_tax'])

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data['order_number']:
            queryset = self.base_queryset.filter(
                number__istartswith=data['order_number'])



        #================= Added by Alex 2019.9.5 ========================
        if not self.request.user.is_superuser and self.request.user.is_staff:
            staff_owners_list = Owner.objects.values('id').filter(user_id=self.request.user.id)
            queryset = queryset.filter(owner_id__in=staff_owners_list)
        #=================================================================



        # override name searching with long first_name and last_name
        if data['name']:
            # If the value is two words, then assume they are first name and
            # last name
            parts = data['name'].split()
            allow_anon = getattr(settings, 'OSCAR_ALLOW_ANON_CHECKOUT', False)

            if len(parts) == 1:
                parts = [data['name'], data['name']]
            else:
                parts = [parts[0], ' '.join(parts[1:])]

            filter = Q(user__first_name__icontains=parts[0])
            filter |= Q(user__last_name__icontains=parts[1])
            if allow_anon:
                filter |= Q(billing_address__first_name__icontains=parts[0])
                filter |= Q(shipping_address__first_name__icontains=parts[0])
                filter |= Q(billing_address__last_name__icontains=parts[1])
                filter |= Q(shipping_address__last_name__icontains=parts[1])

            queryset = queryset.filter(filter).distinct()

        if data['product_title']:
            queryset = queryset.filter(
                lines__title__istartswith=data['product_title']).distinct()

        if data['upc']:
            queryset = queryset.filter(lines__upc=data['upc'])

        if data['partner_sku']:
            queryset = queryset.filter(lines__partner_sku=data['partner_sku'])

        if data['date_from'] and data['date_to']:
            date_to = datetime_combine(data['date_to'], datetime.time.max)
            date_from = datetime_combine(data['date_from'], datetime.time.min)
            queryset = queryset.filter(
                date_placed__gte=date_from, date_placed__lt=date_to)
        elif data['date_from']:
            date_from = datetime_combine(data['date_from'], datetime.time.min)
            queryset = queryset.filter(date_placed__gte=date_from)
        elif data['date_to']:
            date_to = datetime_combine(data['date_to'], datetime.time.max)
            queryset = queryset.filter(date_placed__lt=date_to)

        if data['voucher']:
            queryset = queryset.filter(
                discounts__voucher_code=data['voucher']).distinct()

        if data['payment_method']:
            queryset = queryset.filter(
                sources__source_type__code=data['payment_method']).distinct()

        # if data['status']:
        #     queryset = queryset.filter(status=data['status'])
        
        # -----------------------
        # end default oscar filtering

        if data['dosimeter_serial_number']:
            queryset = queryset.filter(
                lines__dosimeters__serial_number=data['dosimeter_serial_number'])

        # partner_order_id
        if data['partner_order_id']:
            queryset = queryset.filter(
                partner_order_id=data['partner_order_id'])

        # partner_id
        if data['partner_id']:
            queryset = queryset.filter(
                lines__partner_id=data['partner_id'])

        # owner_id
        if data['owner_id']:
            queryset = queryset.filter(
                owner_id=data['owner_id'])

        if data['email']:
            queryset = queryset.filter(
                user__email__iexact=data['email']).distinct()

        if data['address']:
            filter = Q(billing_address__search_text__icontains=data['address'])
            filter |= Q(shipping_address__search_text__icontains=data['address'])
            queryset = queryset.filter(filter).distinct()

        if data['phone_number']:
            queryset = queryset.filter(
                user__phone_number__iexact=data['phone_number']).distinct()

        if data['approval_status'] == 'ready_for_approval_and_not_approved':
            queryset = queryset.filter(filter_ready_for_approval_but_not_approved()).distinct()
        elif data['approval_status'] == 'approved':
            queryset = queryset.filter(filter_approved()).distinct()
        elif data['approval_status'] == 'not_ready_for_approval_and_not_approved':
            queryset = queryset.filter(filter_not_ready_for_approval_and_not_approved()).distinct()

        if data['report_status'] == 'sent':
            queryset = queryset.filter(is_report_sent=True).distinct()
        elif data['report_status'] == 'reported':
            queryset = queryset.filter(is_reported_by_partner=True).distinct()
        elif data['report_status'] == 'not reported':
            queryset = queryset.filter(is_reported_by_partner=False).distinct()
        elif data['report_status'] == 'sent_or_reported':
            queryset = queryset.filter(filter_sent_or_reported()).distinct()
        elif data['report_status'] == 'not_sent_and_not_reported':
            queryset = queryset.filter(is_reported_by_partner=False,
                                       is_report_sent=False).distinct()
        elif data['report_status'] == 'sent_and_reported':
            queryset = queryset.filter(is_reported_by_partner=True,
                                       is_report_sent=True).distinct()

        if data['analysis_status'] == 'empty':
            queryset = queryset.filter(filter_empty()).distinct()
        elif data['analysis_status'] == 'no_slip_result':
            queryset = queryset.filter(filter_result_no_slip()).distinct()
        elif data['analysis_status'] == 'no_result_slip':
            queryset = queryset.filter(filter_slip_no_result()).distinct()
        elif data['analysis_status'] == 'partial':
            queryset = queryset.filter(filter_partial()).distinct()

        elif data['weirdness_status'] == 'outlier':
            queryset = queryset.filter(is_weird_outlier=True).distinct()
        elif data['weirdness_status'] == 'level_1_overlap':
            queryset = queryset.filter(is_weird_overlap_1=True).distinct()
        elif data['weirdness_status'] == 'level_2_overlap':
            queryset = queryset.filter(is_weird_overlap_2=True).distinct()
        
        if data['order_status'] == 'not canceled':
            queryset = queryset.filter(~Q(status='canceled')).distinct()
        elif data['order_status'] == 'created':
            queryset = queryset.filter(status='created').distinct()
        elif data['order_status'] == 'issued':
            queryset = queryset.filter(status='issued').distinct()
        elif data['order_status'] == 'delivery_to_client':
            queryset = queryset.filter(status='delivery_to_client').distinct()
        elif data['order_status'] == 'completed':
            queryset = queryset.filter(status='completed').distinct()
        elif data['order_status'] == 'canceled':
            queryset = queryset.filter(status='canceled').distinct()

        if data['shipment_status'] == 'UNKNOWN':
            queryset = queryset.filter(shipment__current_status='').distinct()
#        elif data['shipment_status'] == 'NOT_FAILED':
#            queryset = queryset.filter(~Q(shipment__current_status='FAILED')).distinct()
        elif data['shipment_status'] not in ['does_not_matter', '']:
            queryset = queryset.filter(shipment__current_status=data['shipment_status']).distinct()

        if data['is_exists_accounting'] is not None:
            queryset = queryset.filter(is_exists_accounting=data['is_exists_accounting'])
        if data['is_paid'] is not None:
            queryset = queryset.filter(is_paid=data['is_paid'])

        line_subquery = Line.objects.filter(
            dosimeters__isnull=False,
            order_id=OuterRef('id')
        )
        queryset = queryset.select_related(
            'owner', 'shipment', 'shipment_return',
        ).annotate(
            has_line=Exists(line_subquery)
        ).prefetch_related('lines__dosimeters')
        return queryset

    def get_search_filter_descriptions(self, **kwargs):  # noqa (too complex (19))
        """Describe the filters used in the search.
        These are user-facing messages describing what filters
        were used to filter orders in the search query.
        Returns:
            list of unicode messages
        """
        descriptions = super().get_search_filter_descriptions(**kwargs)

        # Attempt to retrieve data from the submitted form
        # If the form hasn't been submitted, then `cleaned_data`
        # won't be set, so default to None.
        data = getattr(self.form, 'cleaned_data', None)

        if data is None:
            return descriptions

        if data.get('email'):
            descriptions.append(
                _('Customer e-mail is "{email}"').format(
                    email=data['email']
                )
            )

        if data.get('address'):
            descriptions.append(
                _('Customer address (shipping or billing) contains "{address}"').format(
                    address=data['address']
                )
            )

        if data.get('phone_number'):
            descriptions.append(
                _('Customer phone number is "{phone_number}"').format(
                    phone_number=data['phone_number']
                )
            )

        if data.get('approval_status') not in ['does_not_matter', '']:
            descriptions.append(
                _('Approval status is "{approval_status}"').format(
                    approval_status=APPROVAL_STATUS_CHOICES_DICT[data['approval_status']]
                )
            )

        if data.get('report_status') not in ['does_not_matter', '']:
            descriptions.append(
                _('Report status is "{report_status}"').format(
                    report_status=REPORT_STATUS_CHOICES_DICT[data['report_status']]
                )
            )

        if data.get('analysis_status') not in ['does_not_matter', '']:
            descriptions.append(
                _('Analysis status is "{analysis_status}"').format(
                    analysis_status=ANALYSIS_STATUS_CHOICES_DICT[data['analysis_status']]
                )
            )

        if data.get('weirdness_status') not in ['does_not_matter', '']:
            descriptions.append(
                _('Suspect results status is "{analysis_status}"').format(
                    analysis_status=WEIRDNESS_STATUS_CHOICES_DICT[data['weirdness_status']]
                )
            )
        
        if data.get('order_status') not in ['does_not_matter', '']:
            descriptions.append(
                _('Order status is "{order_status}"').format(
                    order_status=ORDER_STATUS_CHOICES_DICT[data['order_status']]
                )
            )
        
        if data.get('shipment_status') not in ['does_not_matter', '']:
            descriptions.append(
                _('Shipment status is "{shipment_status}"').format(
                    shipment_status=SHIPMENT_STATUS_CHOICES_DICT[data['shipment_status']]
                )
            )

        if data.get('dosimeter_serial_number'):
            descriptions.append(
                _('Dosimeter serial number is "{dosimeter_serial_number}"').format(
                    dosimeter_serial_number=data['dosimeter_serial_number']
                )
            )

        if data.get('partner_order_id'):
            descriptions.append(
                _('Partner order id is "{partner_order_id}"').format(
                    partner_order_id=data['partner_order_id']
                )
            )

        if data.get('partner_id'):
            descriptions.append(
                _('Partner is "{partner}"').format(
                    partner=Partner.objects.get(id=data['partner_id'])
                )
            )

        if data.get('owner_id'):
            descriptions.append(
                _('Owner is "{owner}"').format(
                    owner=Owner.objects.get(id=data['owner_id'])
                )
            )

        return descriptions
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['is_superuser'] = self.request.user.is_superuser
        context['is_staff'] = self.request.user.is_staff

        return context



class OrderCreateView(TemplateView):
    template_name = 'dashboard/orders/order_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = (s for s in settings.OSCAR_ORDER_STATUS_PIPELINE)
        context['currencies'] = ('DKK', 'NOK', 'SEK', 'USD', 'EUR')
        context['products'] = Product.objects.filter(
            product_class__name=settings.OSCAR_PRODUCT_TYPE_DOSIMETER)
        context['countries'] = Country.objects.filter(is_shipping_country=True)
        return context
