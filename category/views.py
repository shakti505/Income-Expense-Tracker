from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category
from rest_framework import status
from .serializers import CategorySerializer
from rest_framework.pagination import PageNumberPagination


class CategoryCRUDView(APIView):
    def get(self, request, id=None):
        """
        Handle retrieving categories. If an 'id' is provided, return details of a single category.
        Otherwise, return a paginated list of categories for the authenticated user or all for staff.
        """
        if id:
            try:
                # Staff users can access any category; others only their own
                if request.user.is_staff:
                    category = Category.objects.get(id=id)
                else:
                    category = Category.objects.get(id=id, user=request.user)

                # Check if the category is soft-deleted
                if category.is_deleted:
                    return Response(
                        {"detail": "This category has been deleted."},
                        status=status.HTTP_410_GONE,
                    )

                serializer = CategorySerializer(category)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except Category.DoesNotExist:
                return Response(
                    {
                        "detail": "Category not found or you do not have permission to view it."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # For staff, fetch all categories; others get only their own
        if request.user.is_staff:
            categories = Category.objects.filter(is_deleted=False)
        else:
            categories = Category.objects.filter(
                user=request.user, is_deleted=False
            ) | Category.objects.filter(is_default=True, is_deleted=False)

        if request.user.is_deleted and not request.user.is_staff:
            return Response(
                {"detail": "User is marked as deleted. Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Create a new category for the authenticated user."""
        data = request.data

        # Allow staff to create categories for themselves or other users
        if request.user.is_staff and "user" in data:
            user_id = data.get("user")
            try:
                data["user"] = user_id
            except Exception:
                return Response(
                    {"detail": "Invalid user ID provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data["user"] = request.user.id

        if not request.user.is_staff:
            data["is_default"] = False

        serializer = CategorySerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id=None):
        """
        Update an existing category for the authenticated user or all for staff.
        """
        try:
            if request.user.is_staff:
                category = Category.objects.get(id=id)
            else:
                category = Category.objects.get(id=id, user=request.user)

            # Check if the category is soft-deleted
            if category.is_deleted:
                return Response(
                    {"detail": "This category has been deleted and cannot be updated."},
                    status=status.HTTP_410_GONE,
                )

            # Non-admin users cannot modify 'is_default'
            if not request.user.is_staff:
                request.data["is_default"] = category.is_default

            serializer = CategorySerializer(
                category, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Category.DoesNotExist:
            return Response(
                {
                    "detail": "Category not found or you do not have permission to edit it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, id=None):
        """Soft-delete a category."""
        try:
            # Staff can delete any category, while others can delete only their own
            if request.user.is_staff:
                category = Category.objects.get(id=id)
            else:
                category = Category.objects.get(id=id, user=request.user)

            # Check if the category is already soft-deleted
            if category.is_deleted:
                return Response(
                    {"detail": "This category has already been deleted."},
                    status=status.HTTP_410_GONE,
                )

            # Perform soft-delete
            category.is_deleted = True
            category.save()
            return Response(
                {"detail": "Category deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Category.DoesNotExist:
            return Response(
                {
                    "detail": "Category not found or you do not have permission to delete it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
