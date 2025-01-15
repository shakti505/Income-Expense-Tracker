from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
import calendar
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionCRUDView(APIView):
    def get(self, request, id=None):
        """
        Staff members can view all transactions, regular users can only see their own transactions.
        """
        if request.user.is_staff:
            if id:
                try:
                    transaction = Transaction.objects.get(id=id, is_deleted=False)
                    serializer = TransactionSerializer(transaction)
                    return Response(
                        {
                            "status": "success",
                            "message": "Transaction retrieved successfully.",
                            "transaction": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                except Transaction.DoesNotExist:
                    return Response(
                        {
                            "status": "error",
                            "message": "Transaction not found.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            transactions = Transaction.objects.filter(is_deleted=False)
        else:
            if id:
                try:
                    transaction = Transaction.objects.get(
                        id=id, user=request.user, is_deleted=False
                    )
                    serializer = TransactionSerializer(transaction)
                    return Response(
                        {
                            "status": "success",
                            "message": "Transaction retrieved successfully.",
                            "transaction": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                except Transaction.DoesNotExist:
                    return Response(
                        {
                            "status": "error",
                            "message": "Transaction not found or permission denied.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            transactions = Transaction.objects.filter(
                user=request.user, is_deleted=False
            )

        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginated_transactions = paginator.paginate_queryset(transactions, request)

        serializer = TransactionSerializer(paginated_transactions, many=True)
        return paginator.get_paginated_response(
            {
                "status": "success",
                "message": "Transactions retrieved successfully.",
                "transactions": serializer.data,
            }
        )

    def post(self, request):
        """
        Staff users can't create transactions for themselves. Normal users can create their own transactions.
        """
        if request.user.is_staff:
            return Response(
                {
                    "status": "error",
                    "message": "Staff users cannot create transactions for their own accounts.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        data["user"] = request.user.id
        serializer = TransactionSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Transaction created successfully.",
                    "transaction": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "message": "Transaction creation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, id=None):
        """
        Staff users can update any transaction, while regular users can only update their own transactions.
        """
        try:
            if request.user.is_staff:
                transaction = Transaction.objects.get(id=id, is_deleted=False)
            else:
                transaction = Transaction.objects.get(
                    id=id, user=request.user, is_deleted=False
                )
        except Transaction.DoesNotExist:
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
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Transaction updated successfully.",
                    "transaction": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Transaction update failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, id=None):
        """
        Staff members can delete any transaction, while regular users can only delete their own transactions.
        """
        try:
            if request.user.is_staff:
                transaction = Transaction.objects.get(id=id, is_deleted=False)
            else:
                transaction = Transaction.objects.get(
                    id=id, user=request.user, is_deleted=False
                )
        except Transaction.DoesNotExist:
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


class MonthlyReport(APIView):
    def get(self, request):
        """
        Generate a monthly financial report for  user, showing income, expenses, and balance.
        """

        today = datetime.today()
        year = today.year
        month = today.month
        _, num_days = calendar.monthrange(
            year, month
        )  # To get number of days in this month

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

        for transaction in transactions:
            if transaction.transaction_type == "income":
                total_income += transaction.amount
            elif transaction.transaction_type == "expense":
                total_expense += transaction.amount

        total_balance = total_income - total_expense

        data = {
            "status": "success",
            "message": "Monthly report generated successfully.",
            "total_income": total_income,
            "total_expense": total_expense,
            "total_balance": total_balance,
        }

        return Response(data)
