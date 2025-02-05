from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound, PermissionDenied


class IsStaffUser(BasePermission):
    """
    Custom permission to only allow staff users.
    """

    def has_permission(self, request, view):
        if not request.user.is_staff:
            raise NotFound(detail="Resource access restricted to staff members.")
        return True


class IsStaffOrOwner(BasePermission):
    """
    Custom permission to only allow owners of an object or staff to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if object is active first
        if not obj.is_active:
            if request.user.is_staff:
                raise PermissionDenied(detail="Requested resource is inactive.")
            raise NotFound(detail="Resource not found.")

        # Staff permissions
        if request.user.is_staff:
            return True

        # Owner permissions
        if obj != request.user:
            raise NotFound(detail="Resource not found.")

        return True
