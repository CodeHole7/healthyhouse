from oscar.core.loading import get_model
from rest_framework import filters
from rest_framework import mixins
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from api.partners.serializers import PartnerSerializer

Partner = get_model('partner', 'Partner')


class PartnerViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    permission_classes = (IsAdminUser,)
    # for results with first valid partners
    queryset = Partner.objects.order_by('id')
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    serializer_class = PartnerSerializer
