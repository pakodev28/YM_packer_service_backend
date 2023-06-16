from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from items.models import Cell, CellOrderSku, Order, OrderSku, Sku, Table

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


class CreateOrderSkuSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели OrderSku."""

    sku = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = OrderSku
        fields = ("sku", "amount")


class CreateOrderSerializer(serializers.Serializer):
    """Сериализатор для создания заказа.
    Принимает вложенный сериализатор OrderSkuSerializer.
    """

    skus = CreateOrderSkuSerializer(many=True)

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
    barcode = serializers.CharField()
    order = serializers.CharField()
    table = serializers.SlugRelatedField(
        slug_field="name", queryset=Table.objects.all()
    )
    skus = CellOrderSkuSerializer(many=True)

    def create(self, validated_data):
        barcode = validated_data.get("barcode")
        orderkey = validated_data.get("order")
        table_name = validated_data.get("table")
        skus = validated_data.get("skus")

        cell = get_object_or_404(Cell, barcode=barcode)
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


class CellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cell
        fields = ["barcode", "name"]


class TableForOrderSerializer(serializers.Serializer):
    userid = serializers.UUIDField()
    table_name = serializers.CharField()


class FindOrderSerializer(serializers.Serializer):
    oldest_order = serializers.UUIDField(format="hex_verbose")
    cells = CellSerializer(many=True)


class SkuSerializer(serializers.ModelSerializer):
    help_text = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Sku
        fields = ["sku", "name", "image", "amount", "help_text"]

    def get_help_text(self, sku):
        return sku.help_text

    def get_amount(self, sku):
        order = self.context["order"]
        order_sku = OrderSku.objects.filter(order=order, sku=sku).first()
        if order_sku:
            return order_sku.amount
        return None


class GetOrderSerializer(serializers.ModelSerializer):
    skus = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "orderkey",
            "recommended_cartontype",
            "total_skus_quantity",
            "skus",
        ]

    def get_skus(self, order):
        sku_serializer = SkuSerializer(
            order.sku.all(), many=True, context={"order": order}
        )
        return sku_serializer.data
