from django.conf.urls import url

from api.url_shortener.views import URLShortenerView

urlpatterns = [
    url(r'^create-short-url$', URLShortenerView.as_view(), name='create-short-url'),
]
