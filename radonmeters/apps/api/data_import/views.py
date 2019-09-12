from django.utils.translation import ugettext as _
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from api.data_import.serializers import ImportAppSerializer
from api.data_import.serializers import ImportOrderSerializer
from api.permissions import IsSuperuser
from api.permissions import IsPartnerOrAdmin


class ImportOrderAPIView(CreateAPIView):
    """
    API view for importing data from different partners sites.
    This view use the serializer which implements all needed logic.
    """

    permission_classes = (IsPartnerOrAdmin,)
    serializer_class = ImportOrderSerializer


class ImportAppAPIView(CreateAPIView):
    """
    API view for importing apps.
    """

    permission_classes = (IsSuperuser,)
    serializer_class = ImportAppSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'detail': _('Application was successfully uploaded.'),
            'url': serializer.instance.url})
