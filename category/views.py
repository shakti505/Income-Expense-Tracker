from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category
from rest_framework import status
from .serializers import CategorySerializer
from rest_framework.pagination import PageNumberPagination


class CategoryCRUDView(APIView):
    def get(self, request, id=None):
        """
        Get Categories of user, if user is staff then they can access all the categories of all users.
        Normal users can access their categories and the default category.
        """
        if id:
            try:
                if request.user.is_staff:
                    category = Category.objects.get(id=id)
                else:
                    # Allow normal users to access their own category or a default category by id
                    category = Category.objects.get(
                        id=id,
                        is_deleted=False,
                    )  # No user filter here for default category

                    # Check if the category is deleted or not
                    if category.is_deleted:
                        return Response(
                            {
                                "status": "error",
                                "message": "This category has been deleted and is no longer available.",
                            },
                            status=status.HTTP_410_GONE,
                        )

                    # If it's not a staff user, check if the category is either their own or default
                    if (
                        not request.user.is_staff
                        and category.user != request.user
                        and not category.is_default
                    ):
                        return Response(
                            {
                                "status": "error",
                                "message": "You do not have permission to view this category.",
                            },
                            status=status.HTTP_403_FORBIDDEN,
                        )

                serializer = CategorySerializer(category)
                return Response(
                    {
                        "status": "success",
                        "message": "Category retrieved successfully.",
                        "category": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            except Category.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "We couldn't find the category, or you don't have permission to view it.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # For staff, fetch all categories; others get only their own and the default category
        if request.user.is_staff:
            categories = Category.objects.filter(is_deleted=False)
        else:
            categories = Category.objects.filter(
                user=request.user, is_deleted=False
            ) | Category.objects.filter(is_default=True, is_deleted=False)

        if request.user.is_deleted and not request.user.is_staff:
            return Response(
                {
                    "status": "error",
                    "message": "Your account has been marked as deleted. Access is denied.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)

        return paginator.get_paginated_response(
            {
                "status": "success",
                "message": "Categories retrieved successfully.",
                "categories": serializer.data,
            }
        )

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
                    {
                        "status": "error",
                        "message": "The user ID provided is invalid.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data["user"] = request.user.id

        serializer = CategorySerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Category created successfully.",
                    "category": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "error",
                "message": "Category creation failed. Please check the provided data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, id=None):
        """Update an existing category for the authenticated user or all for staff."""
        try:
            if request.user.is_staff:
                category = Category.objects.get(id=id)
            else:
                category = Category.objects.get(id=id, user=request.user)

            # Check if the category is soft-deleted
            if category.is_deleted:
                return Response(
                    {
                        "status": "error",
                        "message": "This category has been deleted and cannot be updated.",
                    },
                    status=status.HTTP_410_GONE,
                )

            # Non-admin users cannot modify 'is_default', but we ensure it's correct
            if not request.user.is_staff:
                request.data["is_default"] = category.is_default
            else:
                # If staff user is updating, make sure to set is_default to True
                request.data["is_default"] = True

            serializer = CategorySerializer(
                category, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Category updated successfully.",
                        "category": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "status": "error",
                    "message": "Category update failed. Please check the provided data.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Category.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "We couldn't find the category, or you don't have permission to edit it.",
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
                    {
                        "status": "error",
                        "message": "This category has already been deleted.",
                    },
                    status=status.HTTP_410_GONE,
                )

            # Perform soft-delete
            category.is_deleted = True
            category.save()
            return Response(
                {
                    "status": "success",
                    "message": "Category successfully deleted.",
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        except Category.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "We couldn't find the category, or you don't have permission to delete it.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Something went wrong: {str(e)}. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
