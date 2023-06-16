from ast import Or
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from items.models import Cell, Order, Table
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (
    CellSerializer,
    CreateOrderSerializer,
    FindOrderSerializer,
    GetTokenSerializer,
    LoadSkuOrderToCellSerializer,
    SignUpSerializer,
    TableForOrderSerializer,
    GetOrderSerializer,
)

User = get_user_model()


@api_view(("POST",))
@permission_classes((IsAdminUser,))
def sign_up(request):
    """
    Регистрация упаковщика. Доступен только админу.
    """

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(("POST",))
def get_token(request):
    """
    Авторизация пользователя (выдача токена).
    """

    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data["confirmation_code"]
    user = get_object_or_404(User, id=confirmation_code)
    token = str(AccessToken.for_user(user))
    return Response({"token": token}, status=status.HTTP_201_CREATED)


class CreateOrderAPIView(APIView):
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {"orderkey": order.pk, "order_status": order.status},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoadSkuOrderToCellView(APIView):
    def post(self, request):
        serializer = LoadSkuOrderToCellSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Cell order created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FindOrderAPIView(APIView):
    def get(self, request):
        serializer = TableForOrderSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        userid = serializer.validated_data["userid"]
        table_name = serializer.validated_data["table_name"]

        table = get_object_or_404(Table, name=table_name)
        oldest_order_id = (
            Order.objects.filter(
                cellorder_skus__cell__table=table, status="forming"
            )
            .order_by("cellorder_skus__order__created_at")
            .values_list("pk", flat=True)
            .first()
        )

        if not oldest_order_id:
            return Response(
                {"error": "No orders found for the table."},
                status=status.HTTP_404_NOT_FOUND,
            )
        oldest_order = Order.objects.get(pk=oldest_order_id)
        oldest_order.who_id = userid
        oldest_order.status = "collecting"
        oldest_order.save()

        cells = Cell.objects.filter(
            cellorder_skus__order=oldest_order_id
        ).distinct()
        cell_serializer = CellSerializer(cells, many=True)

        data = {"oldest_order": oldest_order_id, "cells": cell_serializer.data}

        find_order_serializer = FindOrderSerializer(data)

        return Response(find_order_serializer.data)


class OrderDetailsAPIView(APIView):
    def get(self, request):
        orderkey = request.GET.get("orderkey")
        order = get_object_or_404(Order, orderkey=orderkey)

        serializer = GetOrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
