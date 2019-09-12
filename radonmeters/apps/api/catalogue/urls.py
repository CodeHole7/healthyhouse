# -*- coding: utf-8 -*-
from rest_framework import routers

from api.catalogue.views import LocationViewSet

router = routers.DefaultRouter()
router.register(
    '', LocationViewSet, base_name='location')

urlpatterns = []
urlpatterns += router.urls
