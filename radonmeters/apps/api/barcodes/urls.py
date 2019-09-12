from django.conf.urls import url

from api.barcodes.views import QRCodeView

urlpatterns = [
    url(r'^create-qr-code$', QRCodeView.as_view(), name='create-qr-code'),
]
