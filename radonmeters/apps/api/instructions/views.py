from oscar.core.loading import get_model
from rest_framework import mixins, serializers
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.catalogue.serializers import OrderedProductDosimeterSerializer
from api.dosimeters.serializers import DosimeterChangeInstructionSerializer
from api.instructions.serializers import InstructionImageSerializer
from api.order.serializers import CustomerInstructionOrderSerializer
from api.order.views import OrderHelper
from instructions.models import InstructionImage, Instruction


Dosimeter = get_model('catalogue', 'Dosimeter')
Line = get_model('order', 'Line')


class InstructionImageViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = InstructionImage.objects.all()
    serializer_class = InstructionImageSerializer
    permission_classes = (IsAdminUser,)


class InstructionViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet):
    queryset = Instruction.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = serializers.Serializer
    instruction = None

    def get_object(self):
        self.instruction = super().get_object()
        return self.instruction

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'instruction': self.instruction
        })
        return context

    @detail_route(methods=['GET'])
    def orders(self, request, pk=None):
        instruction = self.get_object()
        qs = self.paginate_queryset(instruction.orders.all())
        context = self.get_serializer_context()
        serializer = CustomerInstructionOrderSerializer(qs, many=True, context=context)

        return self.get_paginated_response(serializer.data)

    @detail_route(
        methods=['GET'], url_name='generate-pdf-report',
        url_path='orders/(?P<order_pk>[-\w]+)/generate_pdf_report',
        exclude_from_schema=True)  # prevent invalid drf documentation
    def generate_pdf_report(self, request, pk=None, order_pk=None):
        instruction = self.get_object()
        order = get_object_or_404(instruction.orders, **{'pk': order_pk})
        return OrderHelper.generate_pdf_report(order)

    def get_dosimeter_response_serializer(self, instance):
        context = self.get_serializer_context()
        return OrderedProductDosimeterSerializer(instance, context=context)

    @detail_route(
        methods=['GET', 'PATCH'], url_name='dosimeters_detail',
        url_path='dosimeters/(?P<dosimeter_pk>[-\w]+)')
    def dosimeters(self, request, pk=None, dosimeter_pk=None):
        instruction = self.get_object()

        lines = Line.objects.filter(order__in=instruction.orders.all())
        dosimeter = get_object_or_404(Dosimeter.qs_for_lines(lines), **{'pk': dosimeter_pk})

        if self.request.method == 'PATCH':
            return self._dosimeter_update(request, dosimeter)
        return self._dosimeter_retrieve(request, dosimeter)

    def _dosimeter_retrieve(self, request, dosimeter):
        serializer = self.get_dosimeter_response_serializer(dosimeter)
        return Response(serializer.data)

    def _dosimeter_update(self, request, dosimeter):
        context = self.get_serializer_context()
        context.update({
            'user': self.instruction.user
        })
        serializer = DosimeterChangeInstructionSerializer(
            dosimeter, data=request.data, partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        response_serializer = self.get_dosimeter_response_serializer(instance)
        return Response(response_serializer.data)
