import requests
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from config.settings import CHECK_DATA_SCIENTIST, DATA_SCIENTIST_PACK
from users.models import Table, Printer
from items.models import (
    Cell,
    CellOrderSku,
    Order,
    OrderSku,
    Sku,
    CartonType,
)

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
    def request_to_DS(order, skus_data):
        """Метод для взаимодействия с DS.
        Вызывается в методе create."""

        list_of_sku = []
        for item in skus_data:
            product = Sku.objects.get(sku=item["sku"])
            dict_of_sku = {
                "sku": str(item["sku"]),
                "count": item["amount"],
                "size1": str(product.length),
                "size2": str(product.width),
                "size3": str(product.height),
                "weight": str(product.goods_wght),
                "type": list(
                    product.cargotypes.values_list("cargotype", flat=True)
                ),
            }
            list_of_sku.append(dict_of_sku)

        data_for_DS = {"orderId": str(order.orderkey), "items": list_of_sku}
        check_DS = requests.get(CHECK_DATA_SCIENTIST)
        if check_DS.status_code == 200:
            response = requests.post(DATA_SCIENTIST_PACK, json=data_for_DS)
            print(response.json())
            return response.json()
        else:
            # raise serializers.ValidationError("Не валидные данные")
            return {"package": None}

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
        order = Order.objects.create(status="forming")
        for sku_data in skus_data:
            self.create_order_sku(order, sku_data)

        response_from_DS = self.request_to_DS(order, skus_data)
        package = response_from_DS.get("package")
        if package is not None:
            order.recommended_cartontype = get_object_or_404(
                CartonType, cartontype=package
            )
        order.save()
        return order


class CellOrderSkuSerializer(serializers.ModelSerializer):
    sku = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = CellOrderSku
        fields = ["sku", "quantity"]


class LoadSkuOrderToCellSerializer(serializers.Serializer):
    cell_barcode = serializers.UUIDField(format="hex_verbose")
    order = serializers.UUIDField(format="hex_verbose")
    table_name = serializers.SlugRelatedField(
        slug_field="name", queryset=Table.objects.all()
    )
    skus = CellOrderSkuSerializer(many=True)

    def create(self, validated_data):
        cell_barcode = validated_data.get("cell_barcode")
        orderkey = validated_data.get("order")
        table_name = validated_data.get("table_name")
        skus = validated_data.get("skus")

        cell = get_object_or_404(Cell, barcode=cell_barcode)
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

    @staticmethod
    def get_help_text(sku):
        return sku.help_text

    def get_amount(self, sku):
        order = self.context["order"]
        order_sku = OrderSku.objects.filter(order=order, sku=sku).first()
        if order_sku:
            return order_sku.amount
        return None


class CartonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartonType
        fields = ["barcode", "cartontype"]


class GetOrderSerializer(serializers.ModelSerializer):
    skus = serializers.SerializerMethodField()
    recommended_cartontype = CartonTypeSerializer()

    class Meta:
        model = Order
        fields = [
            "orderkey",
            "recommended_cartontype",
            "total_skus_quantity",
            "skus",
        ]

    @staticmethod
    def get_skus(order):
        sku_serializer = SkuSerializer(
            order.skus.all(), many=True, context={"order": order}
        )
        return sku_serializer.data


class OrderSkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderSku
        fields = ["sku", "packaging_number"]


class OrderAddNewDataSerializer(serializers.Serializer):
    orderkey = serializers.UUIDField(format="hex_verbose")
    selected_cartontypes = serializers.ListField(
        child=serializers.UUIDField(format="hex_verbose")
    )
    total_packages = serializers.IntegerField()
    skus = OrderSkuSerializer(many=True)

    def update(self, instance, validated_data):
        orderkey = validated_data.get("orderkey")
        selected_cartontypes = validated_data.get("selected_cartontypes")
        total_packages = validated_data.get("total_packages")
        skus_data = validated_data.get("skus")

        instance.selected_cartontypes.set(selected_cartontypes)

        instance.total_packages = total_packages
        instance.save()

        for sku_data in skus_data:
            sku = sku_data.get("sku")
            packaging_number = sku_data.get("packaging_number")
            OrderSku.objects.filter(order=orderkey, sku=sku).update(
                packaging_number=packaging_number
            )

        return instance


class StatusOrderSerializer(serializers.ModelSerializer):
    orderkey = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = Order
        fields = ("orderkey", "status")

    @staticmethod
    def validate_status(value):
        if value != "collected":
            raise serializers.ValidationError('Status must be "collected"')
        return value


class GetTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ("id", "name", "available")


class SelectTableSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        user = self.context.get("request").user
        table = get_object_or_404(Table, id=validated_data["id"])
        user.table = table
        user.save()
        return table


class SelectPrinterSerializer(serializers.Serializer):
    barcode = serializers.UUIDField(required=True, format="hex_verbose")

    def create(self, validated_data):
        user = self.context.get("request").user
        printer = get_object_or_404(Printer, barcode=validated_data["barcode"])
        user.printer = printer
        user.save()
        return printer
