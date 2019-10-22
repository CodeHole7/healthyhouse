# -*- coding: utf-8 -*-
from rest_framework import routers
from django.conf.urls import url

from api.order.views import DefaultProductViewSet
from api.order.views import DosimeterViewSet
from api.order.views import OrderViewSet
from api.order.views import add_order_note, get_order_note

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


urlpatterns = [
    url(r'^add_order_note/$',
        add_order_note,
        name="add_order_note"),
    url(r'^get_order_note/$',
        get_order_note,
        name="get_order_note"),
]
urlpatterns += router.urls
