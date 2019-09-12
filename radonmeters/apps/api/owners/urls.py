from django.conf.urls import url, include
from rest_framework import routers

from api.owners.views import OwnerViewSet

router = routers.DefaultRouter()
router.register(r'', OwnerViewSet, base_name='owner')

urlpatterns = [
    url(r'^', include(router.urls)),
]
