# urls.py

from django.urls import path
from .views import TransactionListCreateView, TransactionDetailView

urlpatterns = [
    path('', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('<uuid:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
]
