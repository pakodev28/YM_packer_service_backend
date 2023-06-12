# from django.db import transaction
# from rest_framework import serializers
# from items.models import Sku, Order, OrderSku


# class CreateOrderSerializer(serializers.Serializer):
#     skus = serializers.ListField(
#         child=serializers.DictField(
#             child=serializers.CharField(max_length=100), allow_empty=False
#         )
#     )

#     @transaction.atomic
#     def create(self, validated_data):
#         skus_data = validated_data.pop("skus")

#         with transaction.atomic():
#             order = Order.objects.create(status="forming")
#             for sku_data in skus_data:
#                 sku_id = sku_data["sku"]
#                 quantity = int(sku_data["quantity"])

#                 try:
#                     sku = Sku.objects.select_for_update().get(sku=sku_id)
#                 except Sku.DoesNotExist:
#                     raise serializers.ValidationError("Invalid Sku.")

#                 if sku.available_quantity < quantity:
#                     raise serializers.ValidationError(
#                         "Insufficient quantity for Sku."
#                     )

#                 OrderSku.objects.create(
#                     order=order, sku=sku, quantity=quantity
#                 )

#                 sku.available_quantity -= quantity
#                 sku.save()

#         return order

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model


from items.models import Order, OrderSku, Sku

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
        except Sku.DoesNotExist:
            raise serializers.ValidationError("Invalid Sku.")

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
