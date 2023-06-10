from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from .serializers import SignUpSerializer, GetTokenSerializer

User = get_user_model()


@api_view(('POST',))
@permission_classes((IsAdminUser,))
def sign_up(request):
    """
    Регистрация упаковщика. Доступен только админу.
    """

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
def get_token(request):
    """
    Авторизация пользователя (выдача токена).
    """

    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, id=confirmation_code)
    token = str(AccessToken.for_user(user))
    return Response({'token': token}, status=status.HTTP_201_CREATED)
