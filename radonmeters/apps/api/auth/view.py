from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.utils.translation import ugettext as _
from rest_auth.views import LoginView as BaseLoginView
from rest_auth.views import LogoutView as BaseLogoutView
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class LoginView(BaseLoginView):
    """
    Overridden for update response data.
    """
    def get_response(self):
        # This is default realisation.
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {'user': self.user, 'token': self.token}
            serializer = serializer_class(
                instance=data, context={'request': self.request})
        else:
            serializer = serializer_class(
                instance=self.token, context={'request': self.request})

        # Start of custom realisation.
        data = serializer.data
        data['is_superuser'] = self.user.is_superuser
        data['is_staff'] = self.user.is_staff
        data['is_partner'] = self.user.is_partner
        data['is_laboratory'] = self.user.is_laboratory
        return Response(data)


class LogoutView(BaseLogoutView):
    """
    Overridden for not removing auth_token of user after logout request.
    """
    def logout(self, request):
        django_logout(request)
        return Response({"detail": _("Successfully logged out.")})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_token_view(request):
    """
    View for checking that user is authenticated.
    """
    return Response({})
