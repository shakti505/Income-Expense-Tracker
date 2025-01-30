from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import calendar
from .models import Transaction
from .serializers import TransactionSerializer
from utils.pagination import CustomPageNumberPagination
from utils.permissions import IsStaffOrOwner
from utils.responses import (
    validation_error_response,
    success_response,
    success_single_response,
    not_found_error_response,
    permission_error_response,
)

class BaseTransactionView(APIView):
    """
    Base view for common transaction-related functionality.
    """

    permission_classes = [IsStaffOrOwner]

    def get_transaction(self, transaction_id):
        """
        Retrieve a transaction by ID.
        """
        try:
            return Transaction.objects.get(id=transaction_id, is_deleted=False)
        except Transaction.DoesNotExist:
            return None

    def get_transactions_for_user(self, user):
        """
        Retrieve transactions based on user role.
        """
        if user.is_staff:
            return Transaction.objects.filter(is_deleted=False)
        return Transaction.objects.filter(user=user, is_deleted=False)


class ListTransactionsView(BaseTransactionView):
    """
    View for listing transactions.
    Staff can view all transactions, while normal users can only view their own.
    """

    pagination_class = CustomPageNumberPagination

    def get(self, request):
        """
        Retrieve a paginated list of transactions.
        """
        transactions = self.get_transactions_for_user(request.user)
        paginator = self.pagination_class()
        paginated_transactions = paginator.paginate_queryset(transactions, request)
        serializer = TransactionSerializer(paginated_transactions, many=True)
        return success_response(
            
                serializer.data,
            
        )


class CreateTransactionView(BaseTransactionView):
    """
    View for creating transactions.
    Staff users can create transactions for any user.
    """

    def post(self, request):
        """
        Create a new transaction.
        """
        data = request.data
        if not request.user.is_staff:
            # Normal users can only create transactions for themselves
            data["user"] = request.user.id
        else:
            # Staff users can create transactions for any user
            if "user" not in data:
                return Response(
                    {
                       
                        "message": "User ID is required for staff users.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = TransactionSerializer(data=data, context={"request": request})

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Transaction creation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {
                "status": "success",
                "message": "Transaction created successfully.",
                "transaction": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class UpdateDeleteTransactionView(BaseTransactionView):
    """
    View for updating and deleting transactions.
    Staff users can update or delete any transaction.
    """

    def put(self, request, transaction_id):
        """
        Update an existing transaction.
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return Response(
                {
                    "status": "error",
                    "message": "Transaction not found or permission denied.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TransactionSerializer(
            transaction, data=request.data, partial=True, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Transaction update failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {
                "status": "success",
                "message": "Transaction updated successfully.",
                "transaction": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, transaction_id):
        """
        Soft delete a transaction.
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return Response(
                {
                    "status": "error",
                    "message": "Transaction not found or permission denied.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        transaction.is_deleted = True
        transaction.save()
        return Response(
            {
                "status": "success",
                "message": "Transaction deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class GenerateMonthlyReportView(BaseTransactionView):
    """
    View for generating a monthly financial report.
    """

    def get(self, request):
        """
        Generate a monthly financial report for the user.
        """
        today = datetime.today()
        year = today.year
        month = today.month
        _, num_days = calendar.monthrange(year, month)


        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=num_days)

        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_of_month, end_of_month],
            is_deleted=False,
        )

        total_credit = sum(t.amount for t in transactions if t.type == "credit")
        total_debit = sum(t.amount for t in transactions if t.type == "debit")
        total_balance = total_credit - total_debit
        

        return Response(
            {
                "status": "success",
                "message": "Monthly report generated successfully.",
                "total_credit": total_credit,
                "total_debit": total_debit,
                "total_balance": total_balance,
            }
        )
