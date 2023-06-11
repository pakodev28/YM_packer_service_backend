import uuid

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


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
    """Сериализатор промежуточной модели OrderSku.
    Применяется, как поле в сериализаторе OrderSerializer.
    На вход принимает 2 поля:
        - id
        - amount.
    """

    id = serializers.UUIDField(format='hex')

    class Meta:
        model = OrderSku
        fields = ('id',
                  'amount')


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
        """Метод для создания объектов модели OrderSku (промежуточная модель).
        """
        for element in skus:
            main_sku = get_object_or_404(Sku, sku=element['id'])
            if main_sku.quantity >= element['amount']:
                OrderSku.objects.create(sku=main_sku,
                                        order=order,
                                        amount=element['amount'])
                main_sku.quantity -= element['amount']
            else:
                raise  # TODO надо выбросить исключение типа товары закончились

    def create(self, validated_data):
        skus = validated_data.pop('sku')
        order = Order.objects.create(status='forming')
        self.create_order_sku(order, skus)

        return order
