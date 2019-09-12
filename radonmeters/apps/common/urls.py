# -*- coding: utf-8 -*-

from django.conf.urls import url

from common.utils import is_radosure
from common.views import ConsultationRequestView
from common.views import ContactUsRequestView
from common.views import HealthCheckView
from common.views import HomeView
from common.views import PromoRadonView
from common.views import SubscribeRequestView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^checker/$', HealthCheckView.as_view()),
]

if not is_radosure():
    urlpatterns += [
        url(r'^radon/$', PromoRadonView.as_view(), name='promo_radon'),
        url(r'^subscribe-request/$',
            SubscribeRequestView.as_view(),
            name='create_subscribe_request'),
        url(r'^consultation-request/$',
            ConsultationRequestView.as_view(),
            name='create_consultation_request'),
        url(r'^contact-us/$',
            ContactUsRequestView.as_view(),
            name='contact_us_request'),
    ]
