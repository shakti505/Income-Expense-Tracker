from django.urls import path

from .views import TransactionCRUDView

urlpatterns = [
    path(
        "<uuid:id>/",
        TransactionCRUDView.as_view(),
        name="transaction-update-delete",
    ),
    path(
        "",
        TransactionCRUDView.as_view(),
        name="transaction-list-create",
    ),
]
