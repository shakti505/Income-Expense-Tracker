from django.urls import path
from transaction.views import MonthlyReport
from .views import (
    UserCreateView,
    LoginView,
    LogoutView,
    GetUpdateDeleteUserView,
    UpdatePasswordUserView,
)

urlpatterns = [
    path("auth/register/", UserCreateView.as_view(), name="user-signup"),
    path("auth/login/", LoginView.as_view(), name="user-login"),
    path("auth/logout/", LogoutView.as_view(), name="user-logout"),
    path(
        "user/change-password/",
        UpdatePasswordUserView.as_view(),
        name="change-password",
    ),
    path("user/", GetUpdateDeleteUserView.as_view(), name="user-list-update-delete"),
    path("user/monthly-report/", MonthlyReport.as_view(), name="monthly-report"),
]
