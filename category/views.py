# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Category
# from .serializers import CategorySerializer, CategorySerializer
# from utils.pagination import CustomPageNumberPagination
# from utils.permissions import IsStaffOrOwner
# from rest_framework.exceptions import NotFound
# from utils.responses import (
#     validation_error_response,
#     success_response,
#     not_found_error_response,
#     permission_error_response,
#     success_no_content_response,
# )
# from .tasks import send_email_task


# class CategoryListView(APIView, CustomPageNumberPagination):
#     """Handles listing all categories and creating a new category."""

#     # permission_classes = [IsStaffOrOwner]  # Staff or owner can access

#     def get(self, request):
#         """List all categories for the authenticated user or all categories for staff."""
#         categories = self._get_categories_for_user(request.user)
#         serializer = CategorySerializer(categories, many=True)
#         send_email_task.delay('raushan@gkmit.co', 'Mail Testing', )
#         paginated_categories = self.paginate_queryset(categories, request)
#         return self.get_paginated_response(
#             serializer.data,
#         )
#         # return success_response(data)

#     def post(self, request):
#         """Create a new category for the authenticated user or on behalf of another user if staff."""
#         serializer = CategorySerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return validation_error_response(
#             serializer, status_code=status.HTTP_400_BAD_REQUEST
#         )

#     def _get_categories_for_user(self, user):
#         """Helper method to fetch categories based on user role."""
#         if user.is_staff:
#             return Category.objects.filter()
#         return Category.objects.filter(
#             user=user, is_deleted=False
#         ) | Category.objects.filter(is_default=True, is_deleted=False)


# class CategoryDetailView(APIView):
#     """Handles retrieving, updating, and deleting a specific category."""

#     def get(self, request, id):
#         """Retrieve a specific category by ID."""
#         try:
#             category = self._get_category_by_id(id, request.user)
#             serializer = CategorySerializer(category)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except NotFound as e:
#             return not_found_error_response({str(e)})

#     def put(self, request, id):
#         """Update a specific category by ID."""
#         try:
#             category = self._get_category_by_id(id, request.user)
#             serializer = CategorySerializer(
#                 category, data=request.data, partial=True, context={"request": request}
#             )
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except NotFound as e:
#             return not_found_error_response(
#                 {"detail": str(e)}, status=status.HTTP_404_NOT_FOUND
#             )

#     def delete(self, request, id):
#         """Soft-delete a specific category by ID."""
#         try:
#             # Fetch the category by ID
#             category = Category.objects.get(id=id)

#             # Check if the category is already deleted
#             if category.is_deleted:
#                 return not_found_error_response(
#                     {"message": "Category not found"},
#                     status_code=status.HTTP_404_NOT_FOUND,
#                 )

#             # Check for permission (only staff or owner can delete)
#             if not request.user.is_staff and category.user != request.user:
#                 return not_found_error_response(
#                     {"message": "You do not have permission to delete this category"},
#                 )

#             # Perform soft-delete
#             category.is_deleted = True
#             category.save()

#             # Return a successful response with no content
#             return success_no_content_response()

#         except Category.DoesNotExist:
#             # Handle case where category doesn't exist
#             return not_found_error_response({ "Category not found"})

#     def _get_category_by_id(self, category_id, user):
#         """Helper method to retrieve a category by ID based on user role."""
#         try:
#             category = Category.objects.get(id=category_id)
#             if not user.is_staff and category.user != user:
#                 raise NotFound(
#                     "Category not found or you don't have permission to access it"
#                 )
#             return category
#         except Category.DoesNotExist:
#             raise NotFound("Category not found")

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
from .tasks import send_email_task


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
        send_email_task.delay('raushan@gkmit.co', 'Mail Testing')
        
        # Handle pagination
        paginated_categories = self.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        
        return success_response(
             serializer.data,
            # "count": self.page.paginator.count,
            # "next": self.get_next_link(),
            # "previous": self.get_previous_link()
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