from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from common.templatetags.base_context import site_url

import qrcode
import qrcode.image.svg

from url_shortener.models import make_short_url_id

class URLShortenerView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        if 'url' not in request.query_params:
            raise serializers.ValidationError('url: this query parameter must be supplied.')
        url = request.query_params['url']
        short_url = site_url() + reverse('url_shortener:short_url', kwargs={'short_id': make_short_url_id(url)})
        return Response({
            'short_url': short_url,
            'original_url': url})