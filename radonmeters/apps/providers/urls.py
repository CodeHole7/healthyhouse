# -*- coding: utf-8 -*-
from django.conf.urls import url, include


urlpatterns = [
    url(r'^stripe/', include('radonmeters.apps.providers.stripe_app.urls', namespace='stripe_app')),
]
