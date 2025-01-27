from django.urls import path

from transaction.views import GenerateMonthlyReportView
from .views import (
    UserCreateView,
    LoginView,
    LogoutView,
    UserProfileView,
    UpdatePasswordView,
    UserListView,
)

urlpatterns = [
    path("auth/register/", UserCreateView.as_view(), name="user-signup"),
    path("auth/login/", LoginView.as_view(), name="user-login"),
    path("auth/logout/", LogoutView.as_view(), name="user-logout"),
    path(
        "users/update-password/<uuid:id>/",
        UpdatePasswordView.as_view(),
        name="update-password",
    ),
    path("users/<uuid:id>/", UserProfileView.as_view(), name="user-detail"),
    path("users/", UserListView.as_view(), name="get_all_users"),
    path(
        "users/monthly-report/",
        GenerateMonthlyReportView.as_view(),
        name="monthly-report",
    ),
]
