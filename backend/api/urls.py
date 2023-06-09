from django.urls import path
from .views import CreateOrderAPIView

urlpatterns = [
    path(
        "create_new_order/",
        CreateOrderAPIView.as_view(),
        name="create_new_order",
    ),
]
