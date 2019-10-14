from constance import config
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation
from oscar.core.loading import get_model
from rest_framework import status
from rest_framework import mixins
from rest_framework.decorators import api_view, list_route
from rest_framework.decorators import permission_classes
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.dosimeters.serializers import DosimeterUpdateSerializer, \
    DosimeterChangeSerializer, DosimeterSerialNumberSerializer
from api.dosimeters.serializers import DosimeterUpdateStatusSerializer, BatchSerializer
from api.permissions import IsLaboratory
from common.tasks import mail_admins_task
from customer.utils import COMM_TYPE_DOSIMETER_REPORT
from customer.utils import get_email_templates
from random import randint
from api.users.serializers import UserSerializer
from django.http import JsonResponse


Dosimeter = get_model('catalogue', 'Dosimeter')
DosimeterNote = get_model('catalogue', 'DosimeterNote')
Batch = get_model('catalogue', 'Batch')
Batch_Dosimeter = get_model('catalogue', 'Batch_Dosimeter')
Order = get_model('order', 'Order')
OrderLine = get_model('order','Line')

@api_view(['POST'])
@permission_classes([IsLaboratory])
def set_dosimeters_results_by_lab(request):
    """ Update Dosimeters by Third part institution """

    is_many = True if isinstance(request.data, list) else False
    serializer = DosimeterUpdateSerializer(
        data=request.data,
        many=is_many)
    current_lang = translation.get_language()

    if serializer.is_valid() and serializer.validated_data:
        if is_many:
            last_item_indicator = serializer.validated_data[-1]
            data_list = serializer.validated_data
        else:
            last_item_indicator = serializer.validated_data
            data_list = [last_item_indicator]
        unavailable__dosimeters = []

        for obj in data_list:
            try:
                dosimeter = Dosimeter.objects.get(serial_number=obj['id'])
            except Dosimeter.DoesNotExist:
                unavailable__dosimeters.append(obj['id'])
            else:
                dosimeter.concentration = obj.get('concentration')
                dosimeter.uncertainty = obj.get('uncertainty')
                dosimeter.status = Dosimeter.STATUS_CHOICES.completed
                dosimeter.save()

                order = dosimeter.line.order

                # If system is approving it and
                # all dosimeters in Order have results from laboratory,
                # send email notification to customer.
                if not config.DOSIMETERS_MANUAL_NOTIFICATIONS \
                        and dosimeter.pdf_report_can_be_generated():
                    # Get language for email
                    report_language = \
                        obj.get('language') or config.DOSIMETERS_REPORT_LANGUAGE
                    available_lang_codes = [lang[0] for lang in settings.LANGUAGES]
                    if report_language in available_lang_codes:
                        translation.activate(report_language)

                    # Try to find template in db or stored on drive...
                    try:
                        email_templates = get_email_templates(
                            comm_type=COMM_TYPE_DOSIMETER_REPORT)
                        dosimeter.line.order.user.email_user(
                            subject=email_templates.get('subject'),
                            message=email_templates.get('message'),
                            html_message=email_templates.get('html_message'),
                            from_email=order.get_from_email(),
                            connection=order.get_connection(),
                        )
                    # ...when it not found, send simple message.
                    except NotImplementedError:
                        dosimeter.line.order.user.email_user(
                            from_email=order.get_from_email(),
                            connection=order.get_connection(),
                            subject=_('We got results from laboratory.'),
                            message=_(
                                'You can generate PDF report for '
                                'order #%s.') % dosimeter.line.order.number)
            finally:
                is_last_dosimeter = obj['id'] == last_item_indicator['id']
                if len(unavailable__dosimeters) > 0 and is_last_dosimeter:
                    ids = '\n'.join('-%s' % d for d in unavailable__dosimeters)
                    mail_admins_task.delay(
                        subject=_('Cannot update dosimeters.'),
                        message=_('Dosimeters with serial numbers:\n%s\nnot found.' % ids))

        translation.activate(current_lang)
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def set_dosimeter_status(request):
    """ Update Dosimeter status by Admin """

    serializer = DosimeterUpdateStatusSerializer(data=request.data)

    if serializer.is_valid():
        serial_number = serializer.validated_data.get('serial_number')
        try:
            dosimeter = Dosimeter.objects.get(serial_number=serial_number)
        except Dosimeter.DoesNotExist:
            mail_admins_task.delay(
                subject=_('Cannot update dosimeter status.'),
                message=_('Dosimeter with serial number: %s not found' % serial_number))
            return Response({
                'serial_number': [_('A valid dosimeter serial number is required')]},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            dosimeter.status = Dosimeter.STATUS_CHOICES.on_store_side
            dosimeter.save()
            return Response({
                'detail': _('Status has been changed on (%s).') % dosimeter.status})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsLaboratory])

def generate_sensor_barcode(request):
    # get random 8 chipers

    created_serial_numbers = []
    # get dosimeters in 'unknown'
    dosimeters = Dosimeter.objects.all().filter(status='unknown')
    for dosimeter in dosimeters:
        while True:
            random_bar_code = "0"
            for i in range(1,8):
                digit = randint(0,9)
                random_bar_code = random_bar_code + str(digit)
            # check if barcode is unique
            try:
                Dosimeter.objects.get(serial_number=random_bar_code)
            except Dosimeter.DoesNotExist:
                # save serial number to db and set status as 'created'
                dosimeter.status = Dosimeter.STATUS_CHOICES.created
                dosimeter.serial_number = random_bar_code                           
                dosimeter.save()
                created_serial_numbers.append(random_bar_code)
                break
            finally:
                pass


    return Response({'dosimeters': created_serial_numbers})


@api_view(['POST'])
@permission_classes([IsAdminUser])

def add_dosimeter_note(request):
    
    if 'message' in request.data and 'uuid' in request.data:
        message = request.data['message']
        dosimeter_id = request.data['uuid']
        dosimeter_note = DosimeterNote()
        
        try:
            dosimeter = Dosimeter.objects.get(id=dosimeter_id)
            dosimeter_note.dosimeter = dosimeter
        except:   
            return Response({'success': False})

        dosimeter_note.message = message
        dosimeter_note.save()
        return Response({'success': True})

    return Response({'success': False })

@api_view(['GET'])
@permission_classes([IsLaboratory])

def assign_batch(self, requset):

    return Response({'success': True})

    # return Response({'id':dosimeter.id, 'serial_number':dosimeter.serial_number, 'status': dosimeter.status})


class DosimeterViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    queryset = Dosimeter.objects.all()
    serializer_class = DosimeterChangeSerializer
    serializer_update_class = DosimeterUpdateStatusSerializer
    permission_classes = (IsAdminUser,)

    @list_route(methods=['POST'], serializer_class=DosimeterSerialNumberSerializer)
    def search_by_serial_number(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @list_route(methods=['POST'], serializer_class=DosimeterUpdateStatusSerializer)
    def update_status(self, request):
        """
            @Additional description: 
            additional params 
            ========================> (new_batch_description or batch_id) <=======================
            ex: select existing batch case
                {"number":"1231313","status":"shipped_to_distributor","owner_id":4,"batch_id":3}
            \n
            ex: Creating new batch
                {"number":"1231313","status":"shipped_to_distributor","owner_id":4,"new_batch_description":"qwer"}
        """
        serializer = self.serializer_update_class(data=request.data)
        if serializer.is_valid():
            serial_number = serializer.validated_data.get('serial_number')

            try:
                dosimeter = Dosimeter.objects.get(serial_number=serial_number)

                if 'status' in request.data:
                    dosimeter.status = request.data['status']
                    dosimeter.save()
                if 'owner_id' in request.data:
                    
                    if 'new_batch_description' in request.data:
                        batch = Batch(batch_description = request.data['new_batch_description'], 
                            batch_owner_id = request.data['owner_id'])
                        batch.save()

                        try:
                            batch_dosimeter = Batch_Dosimeter.objects.get(dosimeter_id = dosimeter.id)
                            batch_dosimeter.batch_id = batch.id
                            batch_dosimeter.save()
                        except Batch_Dosimeter.DoesNotExist:            
                            batch_dosimeter = Batch_Dosimeter(batch_id = batch.id, dosimeter_id = dosimeter.id)
                            batch_dosimeter.save()
                        
                        return Response({'success': True})
                    elif 'batch_id' in request.data:
                        batch = Batch.objects.get(id = request.data['batch_id'], batch_owner_id = request.data['owner_id'])
                        try:
                            batch_dosimeter = Batch_Dosimeter.objects.get(dosimeter_id = dosimeter.id)
                            batch_dosimeter.batch_id = batch.id
                            batch_dosimeter.save()
                        except Batch_Dosimeter.DoesNotExist:            
                            batch_dosimeter = Batch_Dosimeter(batch_id = batch.id, dosimeter_id = dosimeter.id)
                            batch_dosimeter.save()
                        return Response({'success': True})
                    
                return Response({'success': True})
                
            except Dosimeter.DoesNotExist:
                return Response({'serial_number': [_('A valid dosimeter serial number is required')]},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchViewSet(
    mixins.ListModelMixin,
    GenericViewSet):
    """
    API to get all batch list
    """
    serializer_class = BatchSerializer
    queryset = Batch.objects.all()
    pagination_class = None