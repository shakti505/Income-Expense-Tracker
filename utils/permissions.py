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

from rest_framework import permissions

class IsStaffOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Staff permissions
        if request.method == "GET":
            if request.user.is_staff:
                return True
            return not obj.is_deleted or (obj.user == request.user)

        if request.user.is_staff:
            return not obj.is_deleted
        

        return not obj.is_deleted and obj.user == request.user

# class IsStaffOrOwner(permissions.BasePermission):
#     """
#     Custom permission to allow staff users or owners of the resource.
#     """

#     def has_object_permission(self, request, view, obj):
#         if not (request.user.is_staff or obj == request.user):
#             raise NotFound(detail="This page not found.")
#         return True
