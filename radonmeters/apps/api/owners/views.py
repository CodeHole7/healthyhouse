from oscar.core.loading import get_model
from rest_framework import filters
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser

from api.owners.serializers import OwnerSerializer
from owners.models import Owner

Dosimeter = get_model('catalogue', 'Dosimeter')


class OwnerViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = Owner.objects.all()
    # pagination_class = None
    serializer_class = OwnerSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('id', 'email')
    search_fields = ('first_name', 'last_name', 'email')
