import base64
import datetime
import json
import zipfile
from collections import OrderedDict
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject

from io import BytesIO

from constance import config
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from django.utils import timezone
from oscar.apps.dashboard.orders.forms import OrderSearchForm
from oscar.apps.order.exceptions import InvalidOrderStatus
from oscar.core.loading import get_model
from oscar.core.utils import datetime_combine
from rest_framework import filters
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.catalogue.serializers import DefaultProductChangeSerializer
from api.catalogue.serializers import DosimeterChangeSerializer
from api.order.serializers import OrderDetailSerializer, OrderApproveSerializer, OrderAccountingLedgerSerializer, OrderExternalReportSerializer, OrderDosimeterDetailSerializer
from api.order.serializers import OrderListSerializer, OrderShipmentSerializer, LineItemSerializer, LineSerializer, OrderUpdateSerializer
from common.utils import create_invoice_pdf
from customer.utils import COMM_TYPE_DOSIMETER_REPORT, COMM_TYPE_LABEL, COMM_TYPE_RETURN_LABEL, COMM_TYPE_INVOICE
from deliveries.client import create_label_request, create_shipment_request, create_shipment_return
from instructions.models import InstructionTemplate
from order.models import ORDER_NOT_FULL, ORDER_IS_WEIRD, ORDER_NO_DOSIMETERS, ORDER_IS_WEIRD


#============ Added by Alex M. 2019.9.18 =============#
Owner = get_model('owners', 'Owner')
Shipment = get_model('deliveries', 'Shipment')
ShipmentReturn = get_model('deliveries', 'ShipmentReturn')
#============ ========================= =============#
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
Dosimeter = get_model('catalogue', 'Dosimeter')
DefaultProduct = get_model('catalogue', 'DefaultProduct')
Instruction = get_model('instructions', 'Instruction')

class OrderHelper:

    @staticmethod
    def generate_pdf_report(obj):
        if obj.dosimeters_pdf_report_can_be_generated:
            # Prepare data.
            file_data = obj.dosimeters_pdf_report_generate()
            file_name = 'Report for order #%s.pdf' % obj.number

            # Prepare response.
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            response.write(file_data)
            return response
        else:
            # Check that laboratory has posted results for all dosimeters.
            has_data_from_lab = not Dosimeter.objects.filter(
                line__order_id=obj.pk,
                concentration__isnull=True,
                uncertainty__isnull=True,
            ).exists()
            if not has_data_from_lab:
                msg = _(
                    'Report cannot be generated.<br>'
                    'Not all dosimeters have been analysed.<br>'
                    'Try again later.')
                return Response({'detail': msg})

            # Check that customer has added all needed data.
            has_data_from_user = Dosimeter.objects.filter(
                line__order_id=obj.pk,
                measurement_start_date__isnull=False,
                measurement_end_date__isnull=False,
            ).exists()
            if not has_data_from_user:
                msg = _(
                    'Report cannot be generated.<br>'
                    'Not all dosimeters have all needed data, '
                    'please fill blank fields and generate report again.')
                return Response({'detail': msg})

            # Return default error message.
            msg = _('Something went wrong, please try again later.')
            return Response({'detail': msg})


class OrderPageNumberPagination(PageNumberPagination):
    dosimeters_count = 0

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            # new dosimeters count
            ('dosimeters_count', self.dosimeters_count),

            # default values
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class OrderViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    list:
        List of orders.

        Example response
        "dosimeters_count": 1071,
        "count": 370,
        "next": "http://example.com/api/v1/orders/?ordering=date_placed&page=2",
        "previous": null,
        "results": [
                {
                    "id": 130,
                    "number": "100146",
                    "status": "issued",
                    "date_placed": "01-02-2016",
                    "quantity": 5,
                    "shipping_code": "00357128520011035094",
                    "shipping_id": "6677861",
                    "owner": null,
                    "is_reported_by_partner": false,
                    "is_report_sent": false,
                    "is_approved": false,
                    "user_who_approved": null,
                    "approved_date": null,
                    "sent_date": null
                },...]
    """
   
    permission_classes = (IsAdminUser,)
    queryset = Order.objects.all()
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend, filters.OrderingFilter)
    search_fields = ('number',)
    filter_fields = ('status',)
    ordering_fields = ('date_placed',)
    pagination_class = OrderPageNumberPagination

    def filter_queryset(self, queryset):

        #============ Added by Alex M. 2019.9.17 =============#
        if not self.request.user.is_superuser and self.request.user.is_staff:
            staff_owners_list = Owner.objects.values('id').filter(user_id=self.request.user.id)
            queryset = queryset.filter(owner_id__in=staff_owners_list)
        #=====================================================#

        qs = super().filter_queryset(queryset)
        dosimeters_count = qs.aggregate(count=Count('lines__dosimeters'))['count']
        self.pagination_class.dosimeters_count = dosimeters_count
        return qs

    def get_serializer_class(self):
        """
        Chooses and returns serializer, based on current `action`.
        """
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action in ['send_report', 'approve']:
            return serializers.BaseSerializer
        elif self.action in ['create_shipment', 'create_return_shipment', 'send_order_email',]:
            return OrderShipmentSerializer
        elif self.action == 'get_order_detail':
            return OrderDosimeterDetailSerializer
        # r
        else:
            return OrderListSerializer
    
    @detail_route(methods=['GET'], permission_classes=[IsAuthenticated])
    def generate_pdf_report(self, request, pk=None):
        """
        Route for generate PDF report for dosimeters.
        """

        obj = self.get_object()

        # Check that user in request has access to current order.
        if obj.user != request.user and not request.user.is_superuser:
            raise PermissionDenied

        return OrderHelper.generate_pdf_report(obj)

    @detail_route(methods=['PATCH'])
    def change_status(self, request, pk=None):
        """
        Route for changing status of order.

        Right now supports only changing to `issued`,
        so we don't need any body of PATCH request.
        """

        try:
            obj = self.get_object()
            obj.set_status('issued')
        except InvalidOrderStatus:
            msg = _(
                'Status cannot be changed to "issued". '
                'Might not all product items have a serial number.')
            return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': _('Status has been changed to "issued".')})

    @staticmethod
    def _send_report(order):
        msg = order.prepare_email_msg(comm_type=COMM_TYPE_DOSIMETER_REPORT)
        msg.attach(
            filename='PDF Report (Order ID: %s' % order.number,
            content=order.dosimeters_pdf_report_generate(),
            mimetype="application/pdf")
        try:
            msg.send()
        except:
            return Response(
                {'details': _('Something wrong. Please, try again later')},
                status=status.HTTP_400_BAD_REQUEST)

        order.is_report_sent = True
        order.sent_date = timezone.now()
        order.save(update_fields=['is_report_sent', 'sent_date'])

        return Response({'detail': _('Report has been sent to customer.'),
                         'sent_date': order.sent_date.strftime(settings.DATE_FORMAT_REST)})

    @detail_route(methods=['POST'], permission_classes=[IsAdminUser])
    def send_report(self, request, pk=None):
        """
        Route for sending report to customer.

        Only admins be able to initialize this action.
        """
        order = self.get_object()

        error_message = ''
        if not order.dosimeters_pdf_report_can_be_generated:
            error_message = _(
                'PDF Report cannot be generated, '
                'please check dosimeters.')

        if not order.is_approved:
            error_message = _('You need to approve report firstly.')

        # if order.is_reported_by_partner:
        #     error_message = _('This order was reported by partner.')

        if error_message:
            return Response(
                {'details': error_message},
                status=status.HTTP_400_BAD_REQUEST)

        return self._send_report(order)
    
    @detail_route(methods=['POST'], permission_classes=[IsAdminUser],
                  parser_classes=(FormParser, MultiPartParser,))
    def upload_external_report(self, request, pk=None):
        """
        Route for uploading external report.

        Only admins are able to initialize this action.
        """
        order = self.get_object()
        serializer = OrderExternalReportSerializer(instance=order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('External report has been uploaded.')})
    
    @detail_route(methods=['POST'], permission_classes=[IsAdminUser],
                  parser_classes=(FormParser, MultiPartParser))
    def change_use_external_report(self, request, pk=None):
        """
        Route for changing flag `use_external_report` True/False. Only admins are able to change this value.
        """
        order = self.get_object()
        if ('use_external_report' in request.POST) and not order.external_report_pdf:
            return Response({'details': 'You need to upload an external report before using it'},
                            status=status.HTTP_400_BAD_REQUEST)
        order.use_external_report = ('use_external_report' in request.POST)
        order.save()
        return Response({'detail': _('The "use external report" value has been updated.')})

    @detail_route(methods=['POST'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Route for changing flag `is_approved` True/False.

        Only admins be able to change this value.
        """
        order = self.get_object()
        not_weird_override = json.loads(request.POST.get('not_weird_override', 'false'))
        ignore_outlier = json.loads(request.POST.get('ignore_outlier', 'false'))
        ignore_overlap_1 = json.loads(request.POST.get('ignore_overlap_1', 'false'))
        ignore_overlap_2 = json.loads(request.POST.get('ignore_overlap_2', 'false'))
        can_be_approved = order.dosimeters_pdf_report_can_be_generated
        weirdness_can_be_overridden = False
        if order.dosimeters_pdf_report_non_approval_reason == ORDER_IS_WEIRD:
            weirdness_can_be_overridden = True
            if order.is_weird_outlier and not ignore_outlier:
                weirdness_can_be_overridden = False
            if order.is_weird_overlap_1 and not ignore_overlap_1:
                weirdness_can_be_overridden = False
            if order.is_weird_overlap_2 and not ignore_overlap_2:
                weirdness_can_be_overridden = False
            if not_weird_override:
                weirdness_can_be_overridden = True

        if not (can_be_approved or weirdness_can_be_overridden):
            force_approve = False
            if order.dosimeters_pdf_report_non_approval_reason == ORDER_NO_DOSIMETERS:
                details = _('there are no active dosimeters')
            elif order.dosimeters_pdf_report_non_approval_reason == ORDER_NOT_FULL:
                details = _('there are non full dosimeters')
            elif order.dosimeters_pdf_report_non_approval_reason == ORDER_IS_WEIRD:
                details = _('order seems to have suspect results according to the following metrics: ')
                metrics = []
                if order.is_weird_outlier:
                    metrics.append(_('outlier metric'))
                if order.is_weird_overlap_1:
                    metrics.append(_('level 1 floor metric'))
                if order.is_weird_overlap_2:
                    metrics.append(_('level 2 floor metric'))
                details += ', '.join(metrics)
                force_approve = True
            return Response(
                {'details':
                    _('order %s: ') % order.number +
                    _('PDF Report cannot be generated: ') +
                    details,
                 'forceApprove': force_approve},
                status=status.HTTP_400_BAD_REQUEST)

        if weirdness_can_be_overridden:
            # Force approval weird order
            order.not_weird = True
            order.not_weird_explanation = request.POST.get('not_weird_explanation', 'no explanation was provided')

        order.user_who_approved = request.user
        order.is_approved = True
        order.approved_date = timezone.now()
        order.save()
        response_data = OrderApproveSerializer(instance=order).data
        return Response(response_data)

    @detail_route(
        methods=['POST'],
        parser_classes=(MultiPartParser,))
    def invoice_to_accounting(self, request, pk=None):
        """
        Post invoice to accounting system
        """

        order = self.get_object()
        context = {'order': order}
        serializer = OrderAccountingLedgerSerializer(data=request.data, context=context)
        print('\n\n\n\n\n\n\n================================================')
        print(context)
        print('===== Before OrderAccountingLedgerSerializer validateion =====\n\n')
        serializer.is_valid(raise_exception=True)
        print('\n\n================================================')
        print('validate passed sccessfully')
        print('======================================================\n\n\n\n\n\n')
        serializer.save()
        return Response({'detail': 'Order was imported'})

    def _get_filtered_qs(self):

        # Validate request data.
        form = OrderSearchForm(self.request.query_params)
        if form.is_valid():
            data = form.cleaned_data
        else:
            return Order.objects.none()

        # Prepare base queryset.
        queryset = Order.objects.all().prefetch_related('lines__products')

        # Filter by order_id:
        order_ids = self.request.query_params.getlist('order_id')
        if order_ids:
            field = serializers.ListField(child=serializers.IntegerField())
            try:
                field.run_validation(order_ids)
            except serializers.ValidationError:
                return Order.objects.none()
            else:
                queryset = queryset.filter(id__in=order_ids)

        # Filter by order_number:
        if data.get('order_number'):
            queryset = queryset.filter(number__istartswith=data['order_number'])

        # Filter by order_number:
        if data.get('order_numbers'):
            queryset = queryset.filter(number__in=data['order_numbers'])

        # Filter by customer name:
        if data.get('name'):
            parts = data['name'].split()
            allow_anon = getattr(settings, 'OSCAR_ALLOW_ANON_CHECKOUT', False)

            if len(parts) == 1:
                parts = [data['name'], data['name']]
            else:
                parts = [parts[0], parts[1:]]

            query = Q(user__first_name__istartswith=parts[0])
            query |= Q(user__last_name__istartswith=parts[1])
            if allow_anon:
                query |= Q(billing_address__first_name__istartswith=parts[0])
                query |= Q(shipping_address__first_name__istartswith=parts[0])
                query |= Q(billing_address__last_name__istartswith=parts[1])
                query |= Q(shipping_address__last_name__istartswith=parts[1])

            queryset = queryset.filter(query).distinct()

        # Filter by product_title:
        if data.get('product_title'):
            queryset = queryset.filter(
                lines__title__istartswith=data['product_title']).distinct()

        # Filter by upc:
        if data.get('upc'):
            queryset = queryset.filter(lines__upc=data['upc'])

        # Filter by partner_sku:
        if data.get('partner_sku'):
            queryset = queryset.filter(lines__partner_sku=data['partner_sku'])

        # Filter by voucher:
        if data.get('voucher'):
            queryset = queryset.filter(
                discounts__voucher_code=data['voucher']).distinct()

        # Filter by payment_method:
        if data.get('payment_method'):
            queryset = queryset.filter(
                sources__source_type__code=data['payment_method']).distinct()

        # Filter by status:
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])

        # Filter by date_from:
        if data.get('date_from') and data.get('date_to'):
            date_to = datetime_combine(data['date_to'], datetime.time.max)
            date_from = datetime_combine(data['date_from'], datetime.time.min)
            queryset = queryset.filter(date_placed__gte=date_from, date_placed__lt=date_to)
        elif data.get('date_from'):
            date_from = datetime_combine(data['date_from'], datetime.time.min)
            queryset = queryset.filter(date_placed__gte=date_from)
        elif data.get('date_to'):
            date_to = datetime_combine(data['date_to'], datetime.time.max)
            queryset = queryset.filter(date_placed__lt=date_to)

        return queryset

    @staticmethod
    def _generate_reports_pdf(qs):
        data_set = []
        for order in qs:

            # Generate name (without extension)
            if order.partner_order_id:
                file_name = 'report_[%s][%s]' % (order.partner_order_id, order.number)
            else:
                file_name = 'report_[][%s]' % order.number

            # Generate file data.
            if order.use_external_report and order.external_report_pdf:
                data_set.append({
                    'file_name': '%s.pdf' % file_name,
                    'file_data': order.external_report_pdf.read()})
            elif order.dosimeters_pdf_report_can_be_generated:
                data_set.append({
                    'file_name': '%s.pdf' % file_name,
                    'file_data': order.dosimeters_pdf_report_generate()})

        return data_set

    def _generate_invoices_pdf(self, qs):
        data_set = []
        for order in qs:

            # Generate name (without extension)
            if order.partner_order_id:
                file_name = 'invoice_[%s][%s]' % (order.partner_order_id, order.number)
            else:
                file_name = 'invoice_[][%s]' % order.number

            # Generate file data.
            context = {
                'user': self.request.user,
                'site': get_current_site(self.request),
                'order': order,
                'lines': order.lines.all(),
                'config': config}
            data_set.append({
                'order': order,
                'file_name': '%s.pdf' % file_name,
                'file_data': create_invoice_pdf(order, context, in_memory=True)})

        return data_set

    @staticmethod
    def _return_zip(file_name: str, data_set: list):
        # Prepare archive.
        io_buffer = BytesIO()

        zf = zipfile.ZipFile(io_buffer, mode='a')

        # Add each file in data_set to archive.
        for pdf_file in data_set:
            zf.writestr(
                pdf_file['file_name'],
                pdf_file['file_data'])

        # Fix for Linux zip files read in Windows.
        for file in zf.filelist:
            file.create_system = 0

        # Close the archive file.
        zf.close()

        # Prepare and return response.
        response = HttpResponse(content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % file_name
        response.write(io_buffer.getvalue())
        return response

    @staticmethod
    def _return_pdf(file_obj):
        # Prepare data.
        file_name = file_obj['file_name']
        file_data = file_obj['file_data']

        # Prepare and return response.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(file_data)
        return response

    @staticmethod
    def _failed_response(message=None):
        message = message or _('No one report can be generated.')
        return Response(
            {'detail': message},
            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['GET'], permission_classes=[IsAdminUser])
    def download_reports_pdf(self, request):
        queryset = self._get_filtered_qs()
        data_set = self._generate_reports_pdf(queryset)

        # Return error, when system cannot generate report.
        if len(data_set) < 1:
            return self._failed_response()

        # Return zip archive with reports (multiply orders).
        elif len(data_set) > 1:
            return self._return_zip('reports', data_set)

        # Return PDF report (single order).
        else:
            return self._return_pdf(data_set[0])

    @list_route(methods=['GET'], permission_classes=[IsAdminUser])
    def generate_invoices_pdf(self, request):
        queryset = self._get_filtered_qs()
        data_set = self._generate_invoices_pdf(queryset)

        # Return error, when system cannot generate report.
        if len(data_set) < 1:
            return self._failed_response()

        # Return zip archive with reports (multiply orders).
        elif len(data_set) > 1:
            return self._return_zip('invoices', data_set)

        # Return PDF report (single order).
        else:
            return self._return_pdf(data_set[0])
    

    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def send_invoices_pdf(self, request):
        queryset = self._get_filtered_qs()
        data_set = self._generate_invoices_pdf(queryset)

        # Return error, when system cannot generate pdf.
        if len(data_set) < 1:
            return self._failed_response()

        # orders which were not sent
        error_orders = []

        for data in data_set:
            order = data['order']
            order.send_email_with_pdf(COMM_TYPE_INVOICE, data['file_name'], data['file_data'])

        if error_orders:
            message = _(
                'Labels for order with number=[{errors}] can not be generated.'.format(
                    errors=', '.join(error_orders)))
            return self._failed_response(message)

        return Response({'detail': _('Invoices has been sent to customers.')})

    def _generate_labels_pdf(self, qs, out_label=True, return_label=False):
        """Create pdf file with all labels"""

        io_buffer = BytesIO()
        # merger = PdfFileMerger()
        writer = PdfFileWriter()
        errors = []
        main_page = None

        for order in qs:
            def add_bytes_to_merger(pdfbytes, page1):
                pdfio = BytesIO()
                pdfio.write(base64.b64decode(pdfbytes))
                # WARNING get only the first page of the result
                page = PdfFileReader(pdfio).getPage(0)
                pdf_width, pdf_height = 842, 595
                page_width = float(page.mediaBox[2])

                if page1:
                    left = round(pdf_width / 2 + (pdf_width / 2 - page_width) / 2, 2)
                    page1.mergeTranslatedPage(page, left, 0, False)
                    writer.addPage(page1)
                    return None
                else:
                    # this is first image on the page
                    new_page = PageObject.createBlankPage(None, pdf_width, pdf_height)
                    left = round((pdf_width / 2 - page_width) / 2, 2)
                    new_page.mergeTranslatedPage(page, left, 0, False)
                    return new_page

            if out_label:
                try:
                    pdfbytes = create_label_request(order.shipping_id)
                    main_page = add_bytes_to_merger(pdfbytes, main_page)
                except ValidationError:
                    errors.append(order.number)
            if return_label:
                try:
                    pdfbytes = create_label_request(order.shipping_return_id)
                    main_page = add_bytes_to_merger(pdfbytes, main_page)
                except ValidationError:
                    errors.append(order.number)

        if main_page:
            writer.addPage(main_page)

        writer.write(io_buffer)
        # merger.write(io_buffer)

        return io_buffer.getvalue(), errors

    def _generate_labels_pdf_for_printer(self, qs, out_label=True, return_label=False):
        """Create pdf file with all labels"""

        io_buffer = BytesIO()
        writer = PdfFileWriter()
        errors = []

        for order in qs:
            def add_bytes_to_merger(pdfbytes):
                pdfio = BytesIO()
                pdfio.write(base64.b64decode(pdfbytes))
                # WARNING get only the first page of the result
                page = PdfFileReader(pdfio).getPage(0)
                writer.addPage(page)
            if out_label:
                try:
                    pdfbytes = create_label_request(order.shipping_id)
                    add_bytes_to_merger(pdfbytes)
                except ValidationError:
                    errors.append(order.number)
            if return_label:
                try:
                    pdfbytes = create_label_request(order.shipping_return_id)
                    add_bytes_to_merger(pdfbytes)
                except ValidationError:
                    errors.append(order.number)

        writer.write(io_buffer)
        return io_buffer.getvalue(), errors

    @list_route(methods=['GET'], permission_classes=[IsAdminUser])
    def generate_labels_pdf(self, request):
        queryset = self._get_filtered_qs()
        qs_labels = queryset.exclude(shipping_id='')

        label_printer = False
        if 'label_printer' in request.GET:
            if request.GET['label_printer'].lower() in['true','1']:
                label_printer = True

        if qs_labels.exists():
            if label_printer:
                file_data, errors = self._generate_labels_pdf_for_printer(queryset)
            else:
                file_data, errors = self._generate_labels_pdf(queryset)

            if errors and len(errors) == qs_labels.count():
                message = _(
                    'Labels for order with number=[{errors}] can not be generated.'.format(
                        errors=', '.join(errors)))
                return self._failed_response(message)

        else:
            message = _('Labels can not be generated.')
            return self._failed_response(message)

        response = HttpResponse(content_type='application/pdf')
        file_name = 'dosimeter_package_labels_{date}.pdf'.format(
            date=timezone.now().strftime('%d-%m-%Y_%H-%M'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(file_data)
        return response

    @list_route(methods=['GET'], permission_classes=[IsAdminUser])
    def generate_return_labels_pdf(self, request):
        queryset = self._get_filtered_qs()
        qs_labels = queryset.exclude(shipping_return_id='')

        label_printer = False
        if 'label_printer' in request.GET:
            if request.GET['label_printer'].lower() in['true','1']:
                label_printer = True

        if qs_labels.exists():
            if label_printer:
                file_data, errors = self._generate_labels_pdf_for_printer(queryset, False, True)
            else:
                file_data, errors = self._generate_labels_pdf(queryset, False, True)
            if errors and len(errors) == qs_labels.count():
                message = _(
                    'Labels for order with number=[{errors}] can not be generated.'.format(
                        errors=', '.join(errors)))
                return self._failed_response(message)

        else:
            message = _('Labels can not be generated.')
            return self._failed_response(message)

        response = HttpResponse(content_type='application/pdf')
        file_name = 'dosimeter_package_return_labels_{date}.pdf'.format(
            date=timezone.now().strftime('%d-%m-%Y_%H-%M'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(file_data)
        return response

    @list_route(methods=['GET'], permission_classes=[IsAdminUser])
    def generate_all_labels_pdf(self, request):
        queryset = self._get_filtered_qs()
        qs_labels = queryset

        if qs_labels.exists():
            file_data, errors = self._generate_labels_pdf(queryset, True, True)

            if errors and len(errors) == qs_labels.count():
                message = _(
                    'Labels for order with number=[{errors}] can not be generated.'.format(
                        errors=', '.join(errors)))
                return self._failed_response(message)

        else:
            message = _('Labels can not be generated.')
            return self._failed_response(message)

        response = HttpResponse(content_type='application/pdf')
        file_name = 'dosimeter_package_all_labels_{date}.pdf'.format(
            date=timezone.now().strftime('%d-%m-%Y_%H-%M'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        response.write(file_data)
        return response

    def _generate_instruction_for_user(self, user, orders):
        file_name = f'instruction_{user.username}'

        # Generate file data.
        instruction = Instruction.create(user, orders)
        return {
            'instruction': instruction,
            'file_name': '%s.pdf' % file_name,
            'file_data': instruction.get_file_content()}

    def _generate_instructions_pdf(self, qs):
        """Generate instructions for orders"""

        data_set = []
        template = InstructionTemplate.active()
        if not template:
            return data_set

        qs_users = qs.order_by('user')

        # init first user and order
        current_user = None
        current_orders = []

        for order in qs_users:
            if current_user == order.user or not current_user:
                # order belong to previous user
                current_orders.append(order)
                current_user = order.user
            else:
                # new user with order
                # Generate name (without extension)
                data_set.append(self._generate_instruction_for_user(current_user, current_orders))

                current_user = order.user
                current_orders = [order]
        if current_user:
            # append the last user
            data_set.append(self._generate_instruction_for_user(current_user, current_orders))

        return data_set

    @list_route(methods=['GET'], permission_classes=[IsAdminUser])
    def generate_instructions_pdf(self, request):
        queryset = self._get_filtered_qs()
        data_set = self._generate_instructions_pdf(queryset)

        # Return error, when system cannot generate report.
        if len(data_set) < 1:
            return self._failed_response()

        # Return zip archive with reports (multiply orders).
        elif len(data_set) > 1:
            return self._return_zip('instructions', data_set)

        # Return PDF report (single order).
        else:
            return self._return_pdf(data_set[0])

    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def send_instructions_pdf(self, request):
        queryset = self._get_filtered_qs()
        data_set = self._generate_instructions_pdf(queryset)

        # Return error, when system cannot generate report.
        if len(data_set) < 1:
            return self._failed_response()

        for data in data_set:
            instruction = data['instruction']
            instruction.send_to_customer()

        return Response({'detail': _('Instructions has been sent to customers.')})

    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def send_labels_pdf(self, request):
        queryset = self._get_filtered_qs()
        qs_labels = queryset.exclude(shipping_id='')
        error_orders = []

        if qs_labels.exists():
            for order in qs_labels:
                qs = Order.objects.filter(id=order.id)
                file_data, errors = self._generate_labels_pdf(qs)
                if errors:
                    error_orders.append(order.number)
                    continue

                # send label
                try:
                    order.send_email_with_pdf(
                        COMM_TYPE_LABEL, 'Label (Order ID: %s' % order.number, file_data)
                except:
                    error_orders.append(order.number)
        else:
            message = _('Labels can not be generated.')
            return self._failed_response(message)

        if error_orders:
            message = _(
                'Labels for order with number=[{errors}] can not be generated.'.format(
                    errors=', '.join(error_orders)))
            return self._failed_response(message)

        return Response({'detail': _('Labels has been sent to customers.')})

    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def send_return_labels_pdf(self, request):
        queryset = self._get_filtered_qs()
        qs_labels = queryset.exclude(shipping_return_id='')
        error_orders = []

        if qs_labels.exists():
            for order in qs_labels:

                qs = Order.objects.filter(id=order.id)
                file_data, errors = self._generate_labels_pdf(qs, False, True)
                if errors:
                    error_orders.append(order.number)
                    continue

                # send label
                try:
                    order.send_email_with_pdf(
                        COMM_TYPE_RETURN_LABEL, 'Return Label (Order ID: %s' % order.number, file_data)
                except:
                    error_orders.append(order.number)

        else:
            message = _('Labels can not be generated.')
            return self._failed_response(message)

        if error_orders:
            message = _(
                'Labels for order with number=[{errors}] can not be generated.'.format(
                    errors=', '.join(error_orders)))
            return self._failed_response(message)

        return Response({'detail': _('Labels has been sent to customers.')})
    

    """
        @Author: Alex 
    """
    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def send_order_email(self, request):
        order_number = request.data['number']

        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            json_response = JsonResponse({'success':False, 'detail':'Order number is not correct'})
            return json_response
        
        order = Order.objects.get(number = order_number)
        order.scan_dosimeters()
        
        json_response = JsonResponse({'success':True, 'detail':'Order Email sent successfully.'})
        return json_response

    
    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def create_shipment(self, request, pk=None):
        order_number = request.data['number']
        
        # Check that order number is valid.
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            json_response = JsonResponse({'success':False, 'detail':'Order number is not correct'})
            return json_response
            # return Response({'detail': _('Order Number is not correct.')})    

        order = Order.objects.get(number = order_number)
        response = create_shipment_request(order)

        shipment = Shipment()
        shipment.order_id = order.id
        shipment.data = response
        shipment.save()

        # order.scan_dosimeters() #send invoice email to customer
        # order.status = "issued"
        # order.save()

        json_response = JsonResponse({'success':True, 'detail':'Shipment created successfully in API.'})
        return json_response
        # return JsonResponse(response)
        # return Response({'detail': _('Shipment Created Successfully in API')})



    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def create_return_shipment(self, request, pk=None):
        order_number = request.data['number']
        
        # Check that order number is valid.
        serializer = self.get_serializer(data=request.data)
        

        if not serializer.is_valid():
            json_response = JsonResponse({'success':False, 'detail':'Order number is not correct.'})
            return json_response
            # return Response({'detail': _('Order Number is not correct.')})    

        order = Order.objects.get(number = order_number)
        response = create_shipment_return(order)

        shipment_return = ShipmentReturn()
        shipment_return.order_id = order.id
        shipment_return.data = response
        shipment_return.save()

        # order.scan_dosimeters()
        # order.status = "issued"
        # order.save()

        json_response = JsonResponse({'success':True, 'detail':'Return shipment created successfully in API.'})
        return json_response
        # return Response({'detail': _('Return Shipment Created Successfully in API')})

    @list_route(methods=['POST'], permission_classes=[IsAdminUser])
    def get_order_detail(self, request, pk=None):
        order_number = request.data['number']
        # status = request.data['status']

        serializer = self.get_serializer(data=request.data['number'])
        
        if serializer.is_valid():
            json_response = JsonResponse({'success':False, 'detail':'Order number is not correct.'})
            return json_response
        
        order = Order.objects.get(number = order_number)
        
        sn = OrderDosimeterDetailSerializer(order)
                
        return Response({'success':True, 'detail':sn.data})
    
@list_route(methods=['POST'], permission_classes=[IsAdminUser])
def get_order_by_status(self, request, pk=None):
    status = request.data['status']

    orders = Order.objects.all(status = status)
    sn = OrderDetailSerializer(orders)
    return Response({'success':True, 'detail':sn})

class DosimeterViewSet(ModelViewSet):
    """
    Viewset for working with instances of `catalogue.Dosimeter`.
    """

    permission_classes = (IsAdminUser,)
    queryset = Dosimeter.objects.all()
    serializer_class = DosimeterChangeSerializer


class DefaultProductViewSet(ModelViewSet):
    """
    Viewset for working with instances of `catalogue.DefaultProduct`.
    """

    permission_classes = (IsAdminUser,)
    queryset = DefaultProduct.objects.all()
    serializer_class = DefaultProductChangeSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)