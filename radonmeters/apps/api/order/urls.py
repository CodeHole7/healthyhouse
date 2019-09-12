# -*- coding: utf-8 -*-
from rest_framework import routers

from api.order.views import DefaultProductViewSet
from api.order.views import DosimeterViewSet
from api.order.views import OrderViewSet

router = routers.DefaultRouter()

# Register `OrderViewSet`.
router.register(
    r'',
    OrderViewSet,
    base_name='order')

# Register `DosimeterViewSet`.
router.register(
    r'dosimeters',
    DosimeterViewSet,
    base_name='dosimeter')

# Register `DefaultProductViewSet`.
router.register(
    r'default-products',
    DefaultProductViewSet,
    base_name='default-product')


urlpatterns = []
urlpatterns += router.urls
