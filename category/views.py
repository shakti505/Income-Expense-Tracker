from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Category
from .serializers import CategorySerializer
from utils.pagination import CustomPageNumberPagination
from utils.responses import (
    validation_error_response,
    success_response,
    success_single_response,
    not_found_error_response,
    success_no_content_response
)
from budget.models import Budget
class CategoryListView(APIView, CustomPageNumberPagination):
    """Handles listing all categories and creating a new category."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all categories for the authenticated user or all categories for staff."""
        try:
            categories = self.get_categories_for_user(request.user)
            category_type = request.query_params.get("type")
            
            if category_type in ["debit", "credit"]:
                categories = categories.filter(type=category_type)
            
            paginated_categories = self.paginate_queryset(categories, request)
            serializer = CategorySerializer(paginated_categories, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """Create a new category for the authenticated user."""
        try:
            serializer = CategorySerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return success_single_response(serializer.data, status_code=status.HTTP_201_CREATED)
            return validation_error_response(serializer.errors)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_categories_for_user(self, user):
        """Get categories based on user role."""
        if user.is_staff:
            return Category.objects.filter(is_deleted=False)
        
        return Category.objects.filter(user=user, is_deleted=False) | Category.objects.filter(is_predefined=True, is_deleted=False)

class CategoryDetailView(APIView):
    """Handles retrieving, updating, and deleting a specific category."""
    permission_classes = [IsAuthenticated]
    
    def get_object(self, id, request):
        """Retrieve the category object and check permissions."""

        category = Category.objects.filter(id=id, is_deleted=False).first()
        if not category:
            raise NotFound("Category not found")
        return category
    def delete_associated_budgets(self, category):
        """Soft delete all budgets associated with this category and user."""
        # Get all budgets associated with this category
        budgets = Budget.objects.filter(category=category, user=category.user, is_deleted=False)
        
        # Soft delete the associated budgets
        budgets.update(is_deleted=True)
    
    def get(self, request, id):
        """Retrieve a specific category."""
        try:
            category = self.get_object(id, request)
            self.check_object_permissions(request, category)
            serializer = CategorySerializer(category)
            return success_single_response(serializer.data)
        except Exception:
            return not_found_error_response()
    def patch(self, request, id):
        """Update a specific category."""
        category = self.get_object(id, request)
        try:
            serializer = CategorySerializer(category, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return success_single_response(serializer.data)
            return validation_error_response(serializer.errors)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        """Soft-delete a specific category."""
        category = self.get_object(id, request)
        try:
            category.is_deleted = True
            category.save()
            self.delete_associated_budgets(category)
            return success_no_content_response()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
