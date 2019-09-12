from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from address.models import MunicipalityRadonRisk


@api_view(['GET'])
@permission_classes([AllowAny])
def municipality_radon_risk(request):
    """
    View for getting municipality radon risk level.
    """

    municipality_name = request.query_params.get('municipality')

    # If name was passed.
    if municipality_name:

        municipality = MunicipalityRadonRisk.objects.filter(
            municipality__icontains=municipality_name).first()

        if municipality:
            rdn_map = {
                0: _('3 of 1000'),
                1: _('1 of 100'),
                2: _('3 of 100'),
                3: _('1 of 10'),
                4: _('3 of 10')}

            try:
                level = rdn_map[municipality.level]
            except KeyError:
                level = None

            return Response({
                'level': level,
                'avglevel': municipality.avglevel,
                'municipality': municipality.municipality})
        else:
            return Response(
                {'detail': _('Data for chosen municipality not found.')},
                status=status.HTTP_400_BAD_REQUEST)

    # Raise error when front-end doesn't pass municipality.
    else:
        return Response(
            {'detail': _('Municipality is required.')},
            status=status.HTTP_400_BAD_REQUEST)
