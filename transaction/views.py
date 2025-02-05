from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from .models import Transaction
from .serializers import TransactionSerializer
from utils.responses import (
    success_response,
    success_no_content_response,
    validation_error_response,
    permission_error_response,
)
from utils.permissions import IsStaffOrOwner
from .swagger_docs import (
    transaction_list_docs,
    transaction_create_docs,
    transaction_detail_docs,
    transaction_update_docs,
    transaction_partial_update_docs,
    transaction_delete_docs,
)


class BaseTransactionView(APIView):
    """
    Base view for transaction-related views. Implements error handling and helper methods.
    """

    def handle_exception(self, exc):
        """Handles exceptions and returns standardized responses."""
        if isinstance(exc, NotFound):
            return permission_error_response(str(exc), status.HTTP_404_NOT_FOUND)
        if isinstance(exc, PermissionDenied):
            return permission_error_response(str(exc), status.HTTP_403_FORBIDDEN)
        if isinstance(exc, ValidationError):
            return validation_error_response(exc.detail)
        return super().handle_exception(exc)


def get_transaction_queryset(user):
    """
    Returns the appropriate queryset based on the user's role.
    Raises no response, only fetches data.
    """
    return (
        Transaction.objects.filter(is_deleted=False)
        if not user.is_staff
        else Transaction.objects.all()
    )


def get_transaction_object(pk, user):
    """
    Fetches a transaction by ID and checks permissions.
    Raises exceptions instead of returning responses.
    """
    transaction = get_object_or_404(Transaction.objects.filter(is_deleted=False), pk=pk)
    if not (user.is_staff or transaction.user == user):
        raise PermissionDenied("You do not have permission to access this transaction.")
    return transaction


# class TransactionListCreateView(BaseTransactionView):
#     permission_classes = [permissions.IsAuthenticated]

#     @transaction_list_docs()
#     def get(self, request):
#         transactions = get_transaction_queryset(request.user)
#         serializer = TransactionSerializer(transactions, many=True)
#         return success_response(data=serializer.data)

#     @transaction_create_docs()
#     def post(self, request):
#         try:
#             serializer = TransactionSerializer(
#                 data=request.data, context={"request": request}
#             )
#             serializer.is_valid(raise_exception=True)

#             user_id = request.data.get("user")
#             if not request.user.is_staff and str(user_id) != str(request.user.id):
#                 raise PermissionDenied("Normal users must pass their own user ID.")

#             serializer.save()
#             return success_response(data=serializer.data)

#         except Exception as exc:
#             return self.handle_exception(exc)


# class TransactionDetailView(BaseTransactionView):
#     permission_classes = [IsStaffOrOwner]

#     @transaction_detail_docs()
#     def get(self, request, pk):
#         try:
#             transaction = get_transaction_object(pk, request.user)
#             serializer = TransactionSerializer(transaction)
#             return success_response(data=serializer.data)
#         except Exception as exc:
#             return self.handle_exception(exc)

#     @transaction_partial_update_docs()
#     def patch(self, request, pk):
#         return self.update_transaction(request, pk, partial=True)

#     def update_transaction(self, request, pk, partial):
#         try:
#             transaction = get_transaction_object(pk, request.user)

#             if "user" in request.data and not request.user.is_staff:
#                 raise PermissionDenied("Normal users cannot update user ID.")

#             serializer = TransactionSerializer(
#                 transaction, data=request.data, partial=partial
#             )
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return success_response(serializer.data)

#         except Exception as exc:
#             return self.handle_exception(exc)

#     def delete(self, request, pk):
#         try:
#             transaction = get_transaction_object(pk, request.user)
#             transaction.is_deleted = True
#             transaction.save()
#             return success_no_content_response()
#         except Exception as exc:
#             return self.handle_exception(exc)

from .tasks import track_and_notify_budget


class TransactionListCreateView(BaseTransactionView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction_list_docs()
    def get(self, request):
        transactions = get_transaction_queryset(request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return success_response(data=serializer.data)

    @transaction_create_docs()
    def post(self, request):
        try:
            serializer = TransactionSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            user_id = request.data.get("user")
            if not request.user.is_staff and str(user_id) != str(request.user.id):
                raise PermissionDenied("Normal users must pass their own user ID.")

            transaction = serializer.save()
            track_and_notify_budget.delay(
                transaction.id
            )  # Track the budget limit after transaction creation

            return success_response(data=serializer.data)

        except Exception as exc:
            return self.handle_exception(exc)


class TransactionDetailView(BaseTransactionView):
    permission_classes = [IsStaffOrOwner]

    @transaction_detail_docs()
    def get(self, request, pk):
        try:
            transaction = get_transaction_object(pk, request.user)
            serializer = TransactionSerializer(transaction)
            return success_response(data=serializer.data)
        except Exception as exc:
            return self.handle_exception(exc)

    @transaction_partial_update_docs()
    def patch(self, request, pk):
        return self.update_transaction(request, pk, partial=True)

    def update_transaction(self, request, pk, partial):
        try:
            transaction = get_transaction_object(pk, request.user)

            if "user" in request.data and not request.user.is_staff:
                raise PermissionDenied("Normal users cannot update user ID.")

            serializer = TransactionSerializer(
                transaction, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            updated_transaction = serializer.save()

            # Track budget limit after updating the transaction

            track_and_notify_budget.delay(updated_transaction.id)

            return success_response(serializer.data)

        except Exception as exc:
            return self.handle_exception(exc)

    def delete(self, request, pk):
        try:
            transaction = get_transaction_object(pk, request.user)
            transaction.is_deleted = True
            transaction.save()

            # Track budget limit after deletion of transaction
            track_and_notify_budget.delay(transaction.id)
            return success_no_content_response()
        except Exception as exc:
            return self.handle_exception(exc)
