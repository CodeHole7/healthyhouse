from django.conf.urls import url

from deliveries.views import DosimeterStatusUpdateView, download_dosimeter_reports_pdf

urlpatterns = [
    url(r'^update-dosimeter-status', DosimeterStatusUpdateView.as_view(), name='update_dosimeter_status'),
    #url(r'^update-dosimeter-status/(?P<serial_number>\d+)', DosimeterStatusUpdateView.as_view(), name='update_dosimeter_status'),
    url(r'^download-dosimeter-reports-pdf/(\d+)$', download_dosimeter_reports_pdf, name='download_dosimeter_reports_pdf'),
]