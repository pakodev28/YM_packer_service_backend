from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from items.models import Cell, Order
from users.models import Table
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .serializers import (
    CellSerializer,
    CreateOrderSerializer,
    FindOrderSerializer,
    GetTokenSerializer,
    LoadSkuOrderToCellSerializer,
    SignUpSerializer,
    GetOrderSerializer,
    OrderAddNewDataSerializer,
    StatusOrderSerializer,
    GetTableSerializer,
    SelectTableSerializer,
    SelectPrinterSerializer,
)

User = get_user_model()


class SignUpApiView(APIView):
    """Регистрация упаковщика.
    Доступен только админу.
    """

    permission_classes = (IsAdminUser,)

    @staticmethod
    def post(request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenApiView(APIView):
    """Авторизация пользователя (выдача токена)."""

    @staticmethod
    def post(request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data["confirmation_code"]
        user = get_object_or_404(User, id=confirmation_code)
        token = str(AccessToken.for_user(user))
        return Response({"token": token}, status=status.HTTP_201_CREATED)


class GetTablesApiView(APIView):
    """Выдача столов."""

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        queryset = Table.objects.all()
        serializer = GetTableSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SelectTableApiView(APIView):
    """Выбор стола"""

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request, pk):
        serializer = SelectTableSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(id=pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SelectPrinterApiView(APIView):
    """Выбор принтера."""

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        serializer = SelectPrinterSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateOrderAPIView(APIView):
    @staticmethod
    def post(request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {"orderkey": order.pk, "order_status": order.status},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoadSkuOrderToCellView(APIView):
    @staticmethod
    def post(request):
        serializer = LoadSkuOrderToCellSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Cell order created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailsAPIView(APIView):
    @staticmethod
    def get(request):
        orderkey = request.GET.get("orderkey")
        order = get_object_or_404(Order, orderkey=orderkey)

        serializer = GetOrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderAddNewDataAPIView(APIView):
    """
    API-представление для обогащения заказа новыми данными.
    """

    @staticmethod
    def patch(request):
        serializer = OrderAddNewDataSerializer(data=request.data)
        if serializer.is_valid():
            orderkey = serializer.validated_data["orderkey"]
            try:
                order = Order.objects.get(orderkey=orderkey)
                serializer.update(order, serializer.validated_data)

                return Response(
                    {"message": "Order has been successfully updated"},
                    status=status.HTTP_200_OK,
                )
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class OrderStatusUpdateAPIView(APIView):
    """
    API-представление для обновления статуса заказа.
    """

    @staticmethod
    def patch(request):
        serializer = StatusOrderSerializer(data=request.data)
        if serializer.is_valid():
            orderkey = serializer.validated_data["orderkey"]
            order_status = serializer.validated_data["status"]

            try:
                order = Order.objects.get(orderkey=orderkey)
                order.status = order_status
                order.save()

                return Response(
                    {
                        "message": "Order status has been successfully updated to collected"
                    },
                    status=status.HTTP_200_OK,
                )
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class FindOrderAPIView(APIView):
    def get(self, request):
        user = self.request.user
        table = user.table

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
        oldest_order.who_id = user.id
        oldest_order.status = "collecting"
        oldest_order.save()

        cells = Cell.objects.filter(
            cellorder_skus__order=oldest_order_id
        ).distinct()
        cell_serializer = CellSerializer(cells, many=True)

        data = {"oldest_order": oldest_order_id, "cells": cell_serializer.data}

        serializer = FindOrderSerializer(data)
        return Response(serializer.data)
