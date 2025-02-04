
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from utils.permissions import IsStaffOrOwner
from utils.responses import (
    success_response,
    success_single_response,
    validation_error_response,
    success_no_content_response,
    not_found_error_response,
    permission_error_response,
    internal_server_error_response
    
    
)
from .models import Budget
from .serializers import BudgetSerializer
from rest_framework import status
from category.models import Category
from django.db.models import Q
from datetime import datetime

class BudgetListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all budgets with optional filters"""
        try:
            # Get query parameters
            category_id = request.query_params.get('category')
            month_year = request.query_params.get('month_year')
            user = request.user
            print(user)
            queryset = self._get_filtered_queryset(category_id, month_year, user)
            serializer = BudgetSerializer(queryset, many=True, context={'request': request})
            return success_response(serializer.data)
            
        except Category.DoesNotExist:
            return not_found_error_response("Category not found")
        except Exception as e:
            return internal_server_error_response(str(e))

    def post(self, request):
        """Create a new budget"""
        try:
            # Validate required field

            category = get_object_or_404(Category, id=request.data.get('category'))
            
            serializer = BudgetSerializer(
                data=request.data,
                context={'request': request}
            )
            print(serializer)
            
            if serializer.is_valid():
                serializer.save()
                return success_single_response(serializer.data)
            return validation_error_response(serializer.errors)
        except Category.DoesNotExist:
            return not_found_error_response("Category not found")
        except Exception as e:
            return internal_server_error_response(str(e))

    def _get_filtered_queryset(self, category_id=None, month_year=None, user=None):
        """Get filtered queryset based on user permissions and filters"""
        queryset = Budget.objects.filter() 
        

        # Apply user filter for non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user, is_deleted=False)

        # Apply category filter
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Apply month-year filter
        if month_year:
            try:
                month, year = month_year.split('-')
                queryset = queryset.filter(
                    month=int(month),
                    year=int(year)
                )
            except ValueError:
                pass

        return queryset.select_related('user', 'category')

class BudgetDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrOwner]

    def get(self, request, pk):
        """Retrieve a specific budget"""
        try:
            budget = self._get_budget_object(pk)
            self.check_object_permissions(request, budget)
            serializer = BudgetSerializer(budget, context={'request': request})
            return success_single_response(serializer.data)
            
        except Budget.DoesNotExist:
            return not_found_error_response("Budget not found")
        except Exception as e:
            return internal_server_error_response(str(e))

    def patch(self, request, pk):
        """Update a budget"""
        try:
            budget = self._get_budget_object(pk)
            print(budget)
            self.check_object_permissions(request, budget)
            serializer = BudgetSerializer(
                budget,
                data=request.data,
                context={'request': request},
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return success_single_response(serializer.data)
            return validation_error_response(serializer.errors)
                
        except Budget.DoesNotExist:
            return not_found_error_response("Budget not found")
        except Exception as e:
            return internal_server_error_response(str(e))

    def delete(self, request, pk):
        """Soft delete a budget"""
        try:
            budget = self._get_budget_object(pk)
            self.check_object_permissions(request, budget)
            budget.is_deleted = True
            budget.save()
            return success_no_content_response()
            
        except Budget.DoesNotExist:
            return not_found_error_response("Budget not found")
        except Exception as e:
            return internal_server_error_response(str(e))

    def _get_budget_object(self, pk):
        """Get budget object with proper filtering"""
        queryset = Budget.objects.filter(is_deleted=False)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        budget = get_object_or_404(queryset, pk=pk)
        
        return budget
 


