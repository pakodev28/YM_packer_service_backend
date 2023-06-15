from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from items.models import Order, OrderSku, Sku, Cell, CellOrderSku, Table

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации упаковщика.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
        )


class GetTokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена (авторизация).
    """

    confirmation_code = serializers.UUIDField(required=True, format="hex")


class OrderSkuSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели OrderSku."""

    sku = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = OrderSku
        fields = ("sku", "amount")


class CreateOrderSerializer(serializers.Serializer):
    """Сериализатор для создания заказа.
    Принимает вложенный сериализатор OrderSkuSerializer.
    """

    skus = OrderSkuSerializer(many=True)

    class Meta:
        model = Order
        fields = ("skus",)

    @staticmethod
    def create_order_sku(order, sku_data):
        sku_id = sku_data["sku"]
        amount = sku_data["amount"]

        try:
            sku = Sku.objects.select_for_update().get(sku=sku_id)
        except Sku.DoesNotExist as exc:
            raise serializers.ValidationError("Invalid Sku.") from exc

        if sku.quantity < amount:
            raise serializers.ValidationError("Insufficient quantity for Sku.")

        OrderSku.objects.create(order=order, sku=sku, amount=amount)
        sku.quantity -= amount
        sku.save()

    @transaction.atomic
    def create(self, validated_data):
        skus_data = validated_data.pop("skus")

        with transaction.atomic():
            order = Order.objects.create(status="forming")

            for sku_data in skus_data:
                self.create_order_sku(order, sku_data)

        return order


class CellOrderSkuSerializer(serializers.ModelSerializer):
    sku = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = CellOrderSku
        fields = ["sku", "quantity"]


class LoadSkuOrderToCellSerializer(serializers.Serializer):
    code = serializers.CharField()
    order = serializers.CharField()
    table = serializers.SlugRelatedField(
        slug_field="name", queryset=Table.objects.all()
    )
    skus = CellOrderSkuSerializer(many=True)

    def create(self, validated_data):
        code = validated_data.get("code")
        orderkey = validated_data.get("order")
        table_name = validated_data.get("table")
        skus = validated_data.get("skus")

        cell = get_object_or_404(Cell, code=code)
        order = get_object_or_404(Order, orderkey=orderkey)
        table = get_object_or_404(Table, name=table_name)

        cell.table = table
        cell.save()

        for element in skus:
            sku_code = element.get("sku")
            quantity = element.get("quantity")

            sku = get_object_or_404(Sku, sku=sku_code)

            CellOrderSku.objects.create(
                cell=cell, sku=sku, order=order, quantity=quantity
            )

        return cell
