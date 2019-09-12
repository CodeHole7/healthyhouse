from oscar.core.loading import get_model
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from api.catalogue.serializers import OrderedProductDosimeterSerializer
from api.order.serializers import CustomerOrderSerializer
from address.models import MunicipalityRadonRisk

from rest_framework.views import APIView
from rest_framework.response import Response

Dosimeter = get_model('catalogue', 'Dosimeter')

class RadonRiskLookupAPIView(APIView):
    """
    View to provide radon risk level based on address
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """
        Return a risk description.
        """
        municipality = request.data['locality']

        
        rdn = MunicipalityRadonRisk.objects.filter(
            municipality__contains = municipality.lower()
        )
        if rdn.count() > 0:
            rdn = rdn[0]
            rdnmap = {
                0: '3 ud af 1000',
                1: '1 ud af 100',
                2: '3 ud af 100',
                3: '1 ud af 10',
                4: '3 ud af 10'
            }
            return Response(
                {
                    'avglevel' : rdn.avglevel,
                    'level' : rdnmap[rdn.level], 
                    'municipality':rdn.municipality
                    }
            )
        else:
            return Response({'municipality':None})

# @api_view()
# def RadonRiskLookupAPIView(request):
#     return Response({"message": "Hello, world!"})

# class RadonRiskLookupAPIView(generics.ListAPIView):
#     """
#     API view for providing radon_risk level based on address
#     """
#     permission_classes = ()
#     serializer_class =
#     #lookup_field = None
#     #lookup_url_kwarg = None
#     def get_queryset(self):
#         """
#         Returns risk overview based on address
#         """
#         return []

class ProfileOrderListAPIView(generics.ListAPIView):
    """
    API view for providing list of customer's orders.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomerOrderSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Returns queryset of all orders created by current user.
        """

        return self.request.user.orders.all().prefetch_related('lines__product')


class DosimeterUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    API view for updating Dosimeter instances by client.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OrderedProductDosimeterSerializer

    def get_queryset(self):
        """
        Returns queryset of all dosimeters ordered by current user.
        """

        return Dosimeter.objects.filter(line__order__user=self.request.user)
