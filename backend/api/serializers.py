import uuid

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
        fields = ('username',
                  'first_name',
                  'last_name',)


class GetTokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена (авторизация).
    """

    confirmation_code = serializers.CharField(required=True, max_length=128)

    @staticmethod
    def validate_confirmation_code(value):
        try:
            uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError('Некорректные данные (карта неисправна), обратитесь к админу')
        return value


class OrderSkuSerializer(serializers.ModelSerializer):
    sku = serializers.UUIDField(format='hex_verbose')

    class Meta:
        model = OrderSku
        fields = ('sku',
                  'quantity')


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заказа.
    Принимает вложенный сериализатор OrderSkuSerializer.
    """
    sku = OrderSkuSerializer(many=True)

    class Meta:
        model = Order
        fields = 'sku'

    @staticmethod
    def create_order_sku(order, skus):
        """Метод для создания объектов модели OrderSku.
        """
        for element in skus:
            main_sku = Sku.objects.get(sku=element['sku'])
            if main_sku.quantity >= element['quantity']:
                OrderSku.objects.create(sku=element['sku'],
                                        order=order,
                                        quantity=element['quantity'])
                main_sku.quantity -= element['quantity']
            else:
                raise  # TODO надо выбросить исключение типа товары закончились

    def create(self, validated_data):
        skus = validated_data.pop('sku')
        order = Order.objects.create(status='forming')
        self.create_order_sku(order, skus)
        return order
