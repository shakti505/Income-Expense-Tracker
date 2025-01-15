from django.urls import path
from transaction.views import MonthlyReport
from .views import (
    UserCreateView,
    LoginView,
    LogoutView,
    GetUpdateDeleteSingleUserView,
    UpdatePasswordUserView,
    GetAllUsersView,
)

urlpatterns = [
    path("auth/register/", UserCreateView.as_view(), name="user-signup"),
    path("auth/login/", LoginView.as_view(), name="user-login"),
    path("auth/logout/", LogoutView.as_view(), name="user-logout"),
    path(
        "users/update-password/<uuid:id>/",
        UpdatePasswordUserView.as_view(),
        name="update-password",
    ),
    path(
        "users/<uuid:id>/", GetUpdateDeleteSingleUserView.as_view(), name="user-detail"
    ),
    path("users/", GetAllUsersView.as_view(), name="get_all_users"),
    path("users/monthly-report/", MonthlyReport.as_view(), name="monthly-report"),
]
