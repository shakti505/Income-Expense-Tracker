from rest_framework import permissions
from rest_framework.exceptions import NotFound


class IsStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow staff users.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_staff):
            raise NotFound(detail=f"This page not found.")
        return True


class IsStaffOrOwner(permissions.BasePermission):
    """
    Custom permission to allow staff users or owners of the resource.
    """

    def has_object_permission(self, request, view, obj):
        if not (request.user.is_staff or obj == request.user):
            raise NotFound(detail="This page not found.")
        return True
