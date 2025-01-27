from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer
from utils.pagination import CustomPageNumberPagination
from utils.permissions import IsStaffUser, IsStaffOrOwner


class CategoryListView(APIView, CustomPageNumberPagination):
    """Handles listing all categories and creating a new category."""

    permission_classes = [IsStaffOrOwner]  # Staff or owner can access

    def get(self, request):
        """List all categories for the authenticated user or all categories for staff."""
        categories = self._get_categories_for_user(request.user)
        paginated_categories = self.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """Create a new category for the authenticated user or on behalf of another user if staff."""
        serializer = CategorySerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_categories_for_user(self, user):
        """Helper method to fetch categories based on user role."""
        if user.is_staff:
            return Category.objects.filter(is_deleted=False)
        return Category.objects.filter(user=user, is_deleted=False) | Category.objects.filter(is_default=True, is_deleted=False)


class CategoryDetailView(APIView):
    """Handles retrieving, updating, and deleting a specific category."""

    permission_classes = [IsStaffOrOwner]  # Staff or owner can access

    def get(self, request, id):
        """Retrieve a specific category by ID."""
        serializer = CategorySerializer(context={"request": request})
        try:
            category = serializer.get_category(id, request.user)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        """Update a specific category by ID."""
        serializer = CategorySerializer(context={"request": request})
        try:
            category = serializer.get_category(id, request.user)
            serializer = CategorySerializer(category, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        """Soft-delete a specific category by ID."""
        serializer = CategorySerializer(context={"request": request})
        try:
            category = serializer.get_category(id, request.user)
            category.is_deleted = True
            category.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)