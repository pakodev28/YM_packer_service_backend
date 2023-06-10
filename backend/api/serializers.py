import uuid

from rest_framework import serializers
from django.contrib.auth import get_user_model

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
