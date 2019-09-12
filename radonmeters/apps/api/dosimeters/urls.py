from django.conf.urls import url
from rest_framework import routers
from api.dosimeters import views as dosimeters_views

urlpatterns = [
    url(r'^set-results/$',
        dosimeters_views.set_dosimeters_results_by_lab,
        name='set_dosimeters_results_by_lab'),

    url(r'^set-status/$',
        dosimeters_views.set_dosimeter_status,
        name='set_dosimeter_status'),

   	url(r'^generate-sensor-barcode/$',
        dosimeters_views.generate_sensor_barcode,
        name='generate_sensor_barcode'),
]

router = routers.DefaultRouter()
router.register('', dosimeters_views.DosimeterViewSet)
urlpatterns += router.urls
