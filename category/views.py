from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category
from rest_framework import status
from .serializers import CategorySerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User


class CategoryCRUDView(APIView):
    def get(self, request):
        """Get a list of categories for the authenticated user, including default categories."""
        categories = Category.objects.filter(
            user=request.user, is_deleted=False
        ) | Category.objects.filter(is_default=True, is_deleted=False)
        if (request.user.is_deleted) & (not request.user.is_staff):
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
        """
        Create a new category for the authenticated user.
        Automatically assigns the logged-in user to the category.
        Only admins can set 'is_default' to True.
        """
        data = request.data

        # Set 'is_default' based on the user's role
        print(request.user.is_staff)
        if request.user.is_staff:
            data["is_default"] = True
        else:
            data["is_defalt"] = False

        serializer = CategorySerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id=None):
        """
        Update an existing category for the authenticated user.
        Users can only update their own categories.
        Only admins can modify the 'is_default' field.
        """
        try:
            # Ensure the user can only modify their own categories
            category = Category.objects.get(id=id, user=request.user, is_deleted=False)
        except Category.DoesNotExist:
            return Response(
                {
                    "detail": "Category not found or you do not have permission to edit it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Non-admin users cannot modify 'is_default'
        if not request.user.is_staff:
            request.data["is_default"] = category.is_default  # Retain original value

        # Serialize and validate data
        serializer = CategorySerializer(
            category, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        try:
            category = Category.objects.get(id=id, user=request.user, is_deleted=False)
        except Category.DoesNotExist:
            return Response(
                {
                    "detail": "Category not found or you do not have permission to delete it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            category.is_deleted = True
            category.save()
            return Response(
                {"detail": "Category deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
