# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from api.views import municipality_radon_risk

urlpatterns = [
    url(r'^auth/',                      include('api.auth.urls',            namespace='auth')),
    url(r'^profile/',                   include('api.profile.urls',         namespace='profile')),
    url(r'^orders/',                    include('api.order.urls',           namespace='orders')),
    url(r'^dosimeters/',                include('api.dosimeters.urls',      namespace='dosimeters')),
    url(r'^data-import/',               include('api.data_import.urls',     namespace='data_import')),
    url(r'^instructions/',              include('api.instructions.urls',    namespace='instructions')),
    url(r'^municipality-radon-risk/$',  municipality_radon_risk,            name     ='municipality_radon_risk'),
    url(r'^owners/',                    include('api.owners.urls',          namespace='owners')),
    url(r'^partners/',                  include('api.partners.urls',        namespace='partners')),
    url(r'^users/',                     include('api.users.urls',           namespace='users')),
    url(r'^locations/',                 include('api.catalogue.urls',       namespace='locations')),
    url(r'^barcodes/',                  include('api.barcodes.urls',        namespace='barcodes')),
    url(r'^url-shortener/',             include('api.url_shortener.urls',   namespace='url_shortener')),
]
