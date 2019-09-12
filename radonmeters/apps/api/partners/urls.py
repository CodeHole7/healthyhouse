# -*- coding: utf-8 -*-
from rest_framework import routers

from api.partners.views import PartnerViewSet

router = routers.DefaultRouter()
router.register(
    '', PartnerViewSet, base_name='partner')

urlpatterns = []
urlpatterns += router.urls
