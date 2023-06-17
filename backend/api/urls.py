from django.urls import path

from .views import create_order, get_tables, get_token, sign_up, select_table, select_printer

urlpatterns = [
    path('sign-up/', sign_up),
    path('login/', get_token),
    path('create-order/', create_order),
    path('tables/', get_tables),
    path('select-table/<int:id>/', select_table),
    path('select-printer/', select_printer)
]
