import io
from django.http import HttpResponse
from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework.views import APIView

from common.templatetags.base_context import site_url

import qrcode
import qrcode.image.svg

from url_shortener.models import make_short_url_id

class QRCodeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        if 'data' not in request.query_params:
            raise serializers.ValidationError('data: this query parameter must be supplied.')
        qr = qrcode.QRCode( 
            version=None, 
            error_correction=qrcode.constants.ERROR_CORRECT_M, 
            box_size=5,
            border=1, 
        )
        data = request.query_params['data']
        if request.query_params.get('shorten_url', None) == 'true':
            data = site_url() + reverse('url_shortener:short_url', kwargs={'short_id': make_short_url_id(data)})
        qr.add_data(data)
        qr.make(fit=True)
        factory = qrcode.image.svg.SvgPathImage
        img = qr.make_image(fill_color="black", back_color="white", image_factory=factory)
        bytes_io = io.BytesIO()
        img.save(bytes_io)
        svg_data = bytes_io.getvalue()
        return HttpResponse(svg_data, content_type='image/svg+xml')