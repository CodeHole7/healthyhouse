from django.conf.urls import url, include
from rest_framework import routers

from api.instructions.views import InstructionImageViewSet
from api.instructions.views import InstructionViewSet

router = routers.DefaultRouter()
router.register(r'images', InstructionImageViewSet, base_name='image')
router.register(r'', InstructionViewSet, base_name='instruction')

urlpatterns = [
    url(r'^', include(router.urls)),
]
