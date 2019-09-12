from django.conf.urls import url

from url_shortener.views import url_redirect

urlpatterns = [
    url(r'^(?P<short_id>.+)$', url_redirect, name='short_url'),
]