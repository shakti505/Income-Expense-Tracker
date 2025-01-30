
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer
from utils.pagination import CustomPageNumberPagination
from utils.permissions import IsStaffOrOwner
from utils.responses import (
    validation_error_response,
    success_response,
    success_single_response,
    not_found_error_response,
    permission_error_response,
)



class BaseCategoryView(APIView):
    """Base view with common category operations."""
    
    def get_category_or_error(self, id, user):
        """Get category by id with permission check."""
        category = Category.objects.filter(id=id, is_deleted=False).first()
        
        if not category:
            return not_found_error_response( "Category not found")
            
        if not user.is_staff and category.user != user:
            return permission_error_response("You do not have permission to access this category")
            
        return category


class CategoryListView(BaseCategoryView, CustomPageNumberPagination):
    """Handles listing all categories and creating a new category."""

    permission_classes = [IsStaffOrOwner]

    def get(self, request):
        """List all categories for the authenticated user or all categories for staff."""
        categories = self._get_categories_for_user(request.user)

        
        # Handle pagination
        paginated_categories = self.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        
        return success_response(
             serializer.data,
        )

    def post(self, request):
        """Create a new category for the authenticated user."""
        serializer = CategorySerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        
        serializer.save()
        return success_single_response(serializer.data, status_code=status.HTTP_201_CREATED)

    def _get_categories_for_user(self, user):
        """Get categories based on user role."""
        if user.is_staff:
            return Category.objects.filter(is_deleted=False)
            
        return Category.objects.filter(
            user=user, 
            is_deleted=False
        ) | Category.objects.filter(
            is_default=True, 
            is_deleted=False
        )


class CategoryDetailView(BaseCategoryView):
    """Handles retrieving, updating, and deleting a specific category."""

    def get(self, request, id):
        """Retrieve a specific category."""
        category = self.get_category_or_error(id, request.user)
        if isinstance(category, Response):
            return category
            
        serializer = CategorySerializer(category)
        return success_single_response(serializer.data)

    def put(self, request, id):
        """Update a specific category."""
        category = self.get_category_or_error(id, request.user)
        if isinstance(category, Response):
            return category
            
        serializer = CategorySerializer(
            category, 
            data=request.data, 
            partial=True, 
            context={"request": request}
        )
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
            
        serializer.save()
        return success_single_response(serializer.data)

    def delete(self, request, id):
        """Soft-delete a specific category."""
        category = self.get_category_or_error(id, request.user)
        if isinstance(category, Response):
            return category
            
        category.is_deleted = True
        category.save()
        
        return success_response(
            {"message": "Category deleted successfully"},
            status_code=status.HTTP_200_OK
        )