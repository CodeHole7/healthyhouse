from oscar.core.loading import get_model
from rest_framework import mixins
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import GenericViewSet

from api.catalogue.paginations import LocationPageNumberPagination
from api.catalogue.serializers import LocationSerializer
from api.permissions import IsPartnerOrAdmin


Location = get_model('catalogue', 'Location')

class LocationViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    API view for locations.
    """
    permission_classes = (IsPartnerOrAdmin,)
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    ordering = Location._meta.ordering
    pagination_class = LocationPageNumberPagination