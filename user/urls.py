from django.urls import path
from transaction.views import TransactionCRUDView, MonthlyReport
from .views import (
    UserCreateView,
    LoginView,
    LogoutView,
    GetUpdateUserView,
    UpdatePasswordUserView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup/", UserCreateView.as_view(), name="user-signup"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("change-password/", UpdatePasswordUserView.as_view(), name="change-password"),
    path("", GetUpdateUserView.as_view()),
    path("monthly-report/", MonthlyReport.as_view(), name="monthly-report"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
