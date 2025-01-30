from django.urls import path
from .views import (
    ListTransactionsView,
    CreateTransactionView,
    UpdateDeleteTransactionView,
    GenerateMonthlyReportView,
    
)

urlpatterns = [
    path("", ListTransactionsView.as_view(), name="list-transactions"),
    path(
        "create/",
        CreateTransactionView.as_view(),
        name="create-transaction",
    ),
    path(
        "transactions/<uuid:transaction_id>/",
        UpdateDeleteTransactionView.as_view(),
        name="update-delete-transaction",
    ),
    path(
        "monthly-report/",
        GenerateMonthlyReportView.as_view(),
        name="generate-monthly-report",
    ),
  
]
