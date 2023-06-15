from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from items.models import Order, OrderSku, Sku
from users.models import Table

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации упаковщика.
    """

    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',)


class GetTokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена (авторизация).
    """

    confirmation_code = serializers.UUIDField(required=True,
                                              format='hex_verbose')


class CreatOrderSkuSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели OrderSku."""

    sku = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = OrderSku
        fields = ("sku", "amount")


class ReadOrderSkuSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='sku.id')
    name = serializers.ReadOnlyField(source='sku.name')
    image = Base64ImageField(source='sku.image')
    goods_wght = serializers.ReadOnlyField(source='sku.goods_wght')

    class Meta:
        model = OrderSku
        fields = ('id', 'name',
                  'image', 'amount',
                  'goods_wght')


class CreateOrderSerializer(serializers.Serializer):
    """Сериализатор для создания заказа.
    Принимает вложенный сериализатор OrderSkuSerializer.
    """

    skus = CreatOrderSkuSerializer(many=True)

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
            order = Order.objects.create(who=self.context.get('request').user,
                                         status="forming")

            for sku_data in skus_data:
                self.create_order_sku(order, sku_data)

        return order

    def to_representation(self, instance):
        return ReadOrderSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ReadOrderSerializer(serializers.ModelSerializer):
    who = serializers.StringRelatedField()
    sku = ReadOrderSkuSerializer(many=True, source='order_sku')
    total_weight = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('orderkey', 'who',
                  'sku', 'status',
                  'whs', 'box_num',
                  'selected_cartontype', 'recommended_cartontype',
                  'sel_calc_cube', 'pack_volume', 'total_weight',
                  'tracking_id', 'pub_date')

    @staticmethod
    def get_total_weight(obj):
        return sum([item.goods_wght for item in obj.sku.all()])


class GetTable(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ("id",
                  "name",
                  "description")


class SelectTable(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Table
        fields = ('id',)

    def create(self, validated_data):
        table = get_object_or_404(Table, id=validated_data['id'])
        table.user = self.context.get('request').user
        table.save()
        return table
