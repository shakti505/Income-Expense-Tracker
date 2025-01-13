from django.urls import path

from .views import CategoryCRUDView

urlpatterns = [
    path("", CategoryCRUDView.as_view(), name="category-list-create"),
    path("<uuid:id>/", CategoryCRUDView.as_view(), name="category-get-update-delete"),
]
