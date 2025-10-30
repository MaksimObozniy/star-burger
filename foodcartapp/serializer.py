from rest_framework import serializers
import phonenumbers

from .models import Order, Product, OrderItem
from django.db import transaction

class OrderItemsListSerializer(serializers.ListSerializer):
    def to_internal_value(self, data):
        if data is None:
            raise serializers.ValidationError('Это поле не может быть пустым.')
        if not isinstance(data, list):
            t = type(data).__name__
            raise serializers.ValidationError(f'Ожидался лист со значениями, но был получен "{t}"')
        if len(data) == 0:
            raise serializers.ValidationError('Этот список не может быть пустым.')
        return super().to_internal_value(data)


class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        error_messages={
            'does_not_exist': 'Недоступный первичный ключ "{pk_value}"',
            'incorrect_type': 'Недопустимый первичный ключ "{input}"',
        },
    )
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        list_serializer_class = OrderItemsListSerializer

class OrderCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    firstname = serializers.CharField(
        allow_blank=False, allow_null=False,
        error_messages={
            'blank': 'Это поле не может быть пустым',
            'null': 'Это поле не может быть пустым',
            'invalid': 'Not a valid string.'
        },
    )
    lastname = serializers.CharField(
        allow_blank=False, allow_null=False,
        error_messages={
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.',
        },
    )
    phonenumber = serializers.CharField(
        allow_blank=False, allow_null=False,
        error_messages={
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.',
        },
    )
    address = serializers.CharField(
        allow_blank=False, allow_null=False,
        error_messages={
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.',
        },
    )

    products = OrderItemInputSerializer(many=True, allow_empty=False, write_only=True)


    def validate_phonenumber(self, value: str):
        try:
            parsed = phonenumbers.parse(value, 'RU')
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError('Введен некорректный номер телефона.')
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError('Введен некорректный номер телефона.')
        return value

    def create(self, validated_data):

        items = validated_data.pop('products')

        with transaction.atomoc():
            order = Order.objects.create(**validated_data)

            for item in items:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                )
            return order
