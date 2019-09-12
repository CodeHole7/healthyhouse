from rest_framework.permissions import BasePermission


class IsLaboratory(BasePermission):
    """
    Allows access only to laboratories.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_laboratory


class IsPartner(BasePermission):
    """
    Allows access only to partners.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_partner


class IsSuperuser(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsPartnerOrAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        user = request.user
        return user.is_superuser or user.is_partner or user.is_staff
