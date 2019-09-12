from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from rest_framework import filters
from rest_framework import mixins
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from api.users.serializers import UserSerializer

Dosimeter = get_model('catalogue', 'Dosimeter')
User = get_user_model()


class UserViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('id', 'email')
    search_fields = ('first_name', 'last_name', 'email')
