from django.urls import path

from .views import (
    CreateOrderAPIView,
    FindOrderAPIView,
    LoadSkuOrderToCellView,
    OrderDetailsAPIView,
    OrderAddNewDataAPIView,
    OrderStatusUpdateAPIView,
)

urlpatterns = [
    path(
        "order/add-packaging-data/",
        OrderAddNewDataAPIView.as_view(),
        name="add-packaging-data",
    ),
    path(
        "order/create/",
        CreateOrderAPIView.as_view(),
        name="create_new_order",
    ),
    path(
        "upload-to-cell/",
        LoadSkuOrderToCellView().as_view(),
        name="upload-to-cell",
    ),
    path("order/find/", FindOrderAPIView.as_view(), name="find-order"),
    path(
        "order/details/", OrderDetailsAPIView.as_view(), name="order-details"
    ),
    path(
        "order/collected/",
        OrderStatusUpdateAPIView.as_view(),
        name="order-collected",
    ),
]
