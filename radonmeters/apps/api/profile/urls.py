# -*- coding: utf-8 -*-
from django.conf.urls import url

from api.profile import views

urlpatterns = [
    url(r'^orders/$',
        views.ProfileOrderListAPIView.as_view(),
        name="orders"),

    url(r'^dosimeters/(?P<pk>[\w-]+)/$',
        views.DosimeterUpdateAPIView.as_view(),
        name="dosimeter_details"),
]
