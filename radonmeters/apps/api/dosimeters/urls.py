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

   	url(r'^generate_sensor_barcode/$',
        dosimeters_views.generate_sensor_barcode,
        name='generate_sensor_barcode'),
        
    url(r'^add_dosimeter_note/$',
        dosimeters_views.add_dosimeter_note,
        name="add_dosimeter_note"),

]

router = routers.DefaultRouter()
router.register(r'^batch', dosimeters_views.BatchViewSet, base_name='batch')
#router.register(r'', dosimeters_views.DosimeterUpdateViewSet, base_name='update_status')
router.register('', dosimeters_views.DosimeterViewSet)
urlpatterns += router.urls
