from django.db import transaction
from rest_framework import serializers
from items.models import Sku, Order, OrderSku


class CreateOrderSerializer(serializers.Serializer):
    skus = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=100), allow_empty=False
        )
    )

    @transaction.atomic
    def create(self, validated_data):
        skus_data = validated_data.pop("skus")

        with transaction.atomic():
            order = Order.objects.create(status="forming")
            for sku_data in skus_data:
                sku_id = sku_data["sku"]
                quantity = int(sku_data["quantity"])

                try:
                    sku = Sku.objects.select_for_update().get(sku=sku_id)
                except Sku.DoesNotExist:
                    raise serializers.ValidationError("Invalid Sku.")

                if sku.available_quantity < quantity:
                    raise serializers.ValidationError(
                        "Insufficient quantity for Sku."
                    )

                OrderSku.objects.create(
                    order=order, sku=sku, quantity=quantity
                )

                sku.available_quantity -= quantity
                sku.save()

        return order
