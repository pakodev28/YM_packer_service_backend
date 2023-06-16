from django.urls import path

from .views import create_order, get_table, get_token, sign_up, select_table

urlpatterns = [
    path('sign-up/', sign_up),
    path('login/', get_token),
    path('create-order/', create_order),
    path('tables/', get_table),
    path('select-table/<int:id>/', select_table)
]
