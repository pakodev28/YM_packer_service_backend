from django.urls import path

from .views import sign_up, get_token

urlpatterns = [
    path('sign-up/', sign_up),
    path('login/', get_token),
]
