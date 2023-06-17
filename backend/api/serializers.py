from pprint import pprint

import requests
from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from items.models import CartonType, Order, OrderSku, Sku
from users.models import Table, Printer

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
    """Сериализатор промежуточной модели OrderSku.
    ДЛЯ POST запроса"""

    sku = serializers.UUIDField(format="hex_verbose")

    class Meta:
        model = OrderSku
        fields = ("sku", "amount")


class ReadOrderSkuSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели OrderSku.
    ДЛЯ GET запроса."""

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
    Принимает вложенный сериализатор CreatOrderSkuSerializer.
    """

    skus = CreatOrderSkuSerializer(many=True)

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
            dict_of_sku = {"sku": str(item['sku']),
                           "count": item['amount'],
                           "size1": str(product.length),
                           "size2": str(product.width),
                           'size3': str(product.height),
                           "weight": str(product.goods_wght),
                           "type": list(product.cargotypes.values_list("cargotype", flat=True))}
            list_of_sku.append(dict_of_sku)

        data_for_DS = {"orderId": str(order.orderkey), "items": list_of_sku}
        check_DS = requests.get("http://localhost:8000/health")
        if check_DS.status_code == 200:  # Проверка на доступность ДС
            response = requests.post("http://localhost:8000/pack", json=data_for_DS)
            return response.json()
        else:
            return 1  # TODO нужно добавить исключение

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
        order = Order.objects.create(who=self.context.get('request').user,
                                     status="forming")
        for sku_data in skus_data:
            self.create_order_sku(order, sku_data)

        response_from_DS = self.request_to_DS(order, skus_data)  # Вытягиваем данные от ДС (коробку)
        pprint(response_from_DS)
        package = response_from_DS.get('package')
        order.recommended_cartontype = get_object_or_404(CartonType, cartontype=package)
        order.save()
        return order

    def to_representation(self, instance):
        return ReadOrderSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ReadOrderSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ордеров.
    Принимает вложенный сериализатор ReadOrderSkuSerializer."""

    who = serializers.StringRelatedField()
    sku = ReadOrderSkuSerializer(many=True, source='order_sku')
    total_weight = serializers.SerializerMethodField()
    recommended_cartontype = serializers.StringRelatedField()

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


class GetTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ("id", "name", 'available')


class SelectTableSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        user = self.context.get('request').user
        table = get_object_or_404(Table, id=validated_data['id'])
        user.table = table
        user.save()
        print(user.table)
        return table


class SelectPrinterSerializer(serializers.Serializer):
    barcode = serializers.UUIDField(required=True, format='hex_verbose')

    def create(self, validated_data):
        user = self.context.get('request').user
        printer = get_object_or_404(Printer, barcode=validated_data['barcode'])
        user.printer = printer
        user.save()
        print(user.printer)
        return printer
