from django.conf.urls import url, include
from rest_framework import routers

from api.users.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet, base_name='user')

urlpatterns = [
    url(r'^', include(router.urls)),
]
