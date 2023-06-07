from rest_framework import serializers
from items.models import Order, Sku


class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = ["sku", "quantity"]


class CreateOrderSerializer(serializers.ModelSerializer):
    skus = SkuSerializer(many=True)

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        skus_data = validated_data.pop("skus")
        order = Order.objects.create(status="forming")

        for sku_data in skus_data:
            sku = Sku.objects.select_for_update().get(sku=sku_data["sku"])
            quantity = sku_data["quantity"]

            if quantity <= 0:
                raise serializers.ValidationError(f"Invalid quantity for Sku {sku.sku}")

            if sku.quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient quantity for Sku {sku.sku}"
                )

            sku.quantity -= quantity
            sku.save()

            order.skus.add(sku, through_defaults={"quantity": quantity})

        return order
