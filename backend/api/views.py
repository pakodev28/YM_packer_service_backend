from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

from items.models import Order
from users.models import Table
from .serializers import (
    CreateOrderSerializer, GetTable, GetTokenSerializer,
    SelectTable, SignUpSerializer, ReadOrderSerializer)

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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_order(request):
    if request.method == 'POST':
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    queryset = Order.objects.all().order_by('pub_date')
    serializer = ReadOrderSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_table(request):
    queryset = get_list_or_404(Table, user=None)
    serializer = GetTable(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def select_table(request, id):
    serializer = SelectTable(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save(id=id)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
