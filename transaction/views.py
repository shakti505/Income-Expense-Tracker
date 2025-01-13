from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
import calendar
from .models import Transaction, User
from .serializers import TransactionSerializer


class TransactionCRUDView(APIView):
    def get(self, request, id=None):
        """
        If `id` is provided, return a single transaction by ID for the authenticated user.
        Otherwise, return a list of transactions for the authenticated user.
        """
        if id:
            try:
                transaction = Transaction.objects.get(
                    id=id, user=request.user, is_deleted=False
                )
                serializer = TransactionSerializer(transaction)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Transaction.DoesNotExist:
                return Response(
                    {"detail": "Transaction not found or permission denied."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Fetch a list of transactions
        transactions = Transaction.objects.filter(user=request.user, is_deleted=False)
        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginated_transactions = paginator.paginate_queryset(transactions, request)

        serializer = TransactionSerializer(paginated_transactions, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a new transaction for the authenticated user.
        Automatically assigns the logged-in user to the transaction.
        """
        data = request.data
        data["user"] = request.user.id
        print(data["user"])
        serializer = TransactionSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id=None):
        """
        Update an existing transaction for the authenticated user.
        The user can only update their own transactions.
        """
        try:
            transaction = Transaction.objects.get(
                id=id, user=request.user, is_deleted=False
            )
        except Transaction.DoesNotExist:
            return Response(
                {"detail": "Transaction not found or permission denied."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TransactionSerializer(
            transaction, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None, **kwargs):
        """
        Soft delete a transaction for the authenticated user.
        """
        try:
            transaction = Transaction.objects.get(
                id=id, user=request.user, is_deleted=False
            )
        except Transaction.DoesNotExist:
            return Response(
                {"detail": "Transaction not found or permission denied."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            transaction.is_deleted = True
            transaction.save()
            return Response(
                {"detail": "Transaction deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MonthlyReport(APIView):
    def get(self, request):
        """
        Generate a monthly financial report for the authenticated user.
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

        total_income = 0
        total_expense = 0
        category_summary = {}
        print(transactions)
        for transaction in transactions:
            if transaction.transaction_type == "income":
                total_income += transaction.amount
            elif transaction.transaction_type == "expense":
                total_expense += transaction.amount

            category_name = (
                transaction.category.name if transaction.category else "Uncategorized"
            )
            category_summary[category_name] = (
                category_summary.get(category_name, 0) + transaction.amount
            )

        total_balance = total_income - total_expense

        data = {
            "total_income": total_income,
            "total_expense": total_expense,
            "total_balance": total_balance,
            "category_summary": category_summary,
        }

        return Response(data)
