from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("user.urls")),
    path("api/transactions/", include("transaction.urls")),
    path("api/categories/", include("category.urls")),
]
