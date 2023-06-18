from django.urls import path

from .views import (
    CreateOrderAPIView,
    FindOrderAPIView,
    LoadSkuOrderToCellView,
    OrderDetailsAPIView,
    OrderAddNewDataAPIView,
    OrderStatusUpdateAPIView,
    get_tables,
    get_token,
    sign_up,
    select_table,
    select_printer,
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

urlpatterns += [
    path("sign-up/", sign_up),
    path("login/", get_token),
    path("tables/", get_tables),
    path("select-table/<int:id>/", select_table),
    path("select-printer/", select_printer),
]
