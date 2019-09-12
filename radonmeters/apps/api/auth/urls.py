# -*- coding: utf-8 -*-
from django.conf.urls import url

from api.auth.view import LoginView
from api.auth.view import LogoutView
from api.auth.view import check_token_view

urlpatterns = (
    url(r'^check-token/$', check_token_view, name='check_token'),
    url(r'^login/$', LoginView.as_view(), name='rest_login'),
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
)
