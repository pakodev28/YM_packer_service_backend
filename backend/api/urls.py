from django.urls import path, include

from .views import (
    CreateOrderAPIView,
    FindOrderAPIView,
    LoadSkuOrderToCellView,
    OrderDetailsAPIView,
    OrderAddNewDataAPIView,
    OrderStatusUpdateAPIView,
    GetTablesApiView,
    GetTokenApiView,
    SignUpApiView,
    SelectTableApiView,
    SelectPrinterApiView,
)

registration = [
    path("sign-up/", SignUpApiView.as_view()),
    path("login/", GetTokenApiView.as_view()),
]

urlpatterns = [
    path("auth/", include(registration)),
    path("tables/", GetTablesApiView.as_view()),
    path("select-table/<int:pk>/", SelectTableApiView.as_view()),
    path("select-printer/", SelectPrinterApiView.as_view()),
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
