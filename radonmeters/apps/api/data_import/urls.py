# -*- coding: utf-8 -*-
from django.conf.urls import url

from api.data_import.views import ImportOrderAPIView
from api.data_import.views import ImportAppAPIView

urlpatterns = [
    url(r'^orders/$', ImportOrderAPIView.as_view(), name='orders'),
    url(r'^apps/$', ImportAppAPIView.as_view(), name='apps'),
]
