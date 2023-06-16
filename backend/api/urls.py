from django.urls import path

from .views import CreateOrderAPIView, LoadSkuOrderToCellView, FindOrderAPIView

urlpatterns = [
    path(
        "create_new_order/",
        CreateOrderAPIView.as_view(),
        name="create_new_order",
    ),
    path(
        "upload-to-cell/",
        LoadSkuOrderToCellView().as_view(),
        name="upload-to-cell",
    ),
    path("find-order/", FindOrderAPIView.as_view(), name="find-order"),
]
