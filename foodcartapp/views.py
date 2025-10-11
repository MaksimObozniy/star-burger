from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Order, OrderItem

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import phonenumbers


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['POST'])
def register_order(request):

    request_data = request.data

    #Проверка продуктов
    if 'products' not in request_data:
        return Response(
            {'products': 'Обязательное поле.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    products = request_data['products']

    if products is None:
        return Response(
            {'products': 'Поле не может быть пустым.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(products, list):
        return Response(
            {'products': f'Ожидался list со значениями, но был получен {type(products).__name__}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(products) == 0:
        return Response(
            {'products': 'Этот список не может быть пустым.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    #Проверка остальных полей

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address']

    #Проверка на присутсвие значений в ключах
    for field in required_fields:
        if field not in request_data:
            return Response(
                {field : 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    #Проверка полей на корректность заполнения
    for field in required_fields:

        field_value = request_data[field]

        if field_value is None:
            return Response(
                {field: 'Это поле не может быть пустым.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(field_value, str):
            return Response(
                {field: 'Not a valid string.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if field_value.strip() == '':
            return Response(
                {field: 'Это поле не может быть пустым.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    #Проверка номера телефона
    phonenumber_data = request_data['phonenumber']

    try:
        parsed_phone = phonenumbers.parse(phonenumber_data, 'RU')
        if not phonenumbers.is_valid_number(parsed_phone):
            return Response(
                {'phonenumber': 'Введен некорректный номер телефона.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except phonenumbers.NumberParseException:
        return Response(
            {'phonenumber': 'Введен некорректный номер телефона.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    #Создание заказа
    order = Order.objects.create(
        firstname=request_data['firstname'],
        lastname=request_data['lastname'],
        phonenumber=request_data['phonenumber'],
        address=request_data['address'],
    )

    for item in products:
        try:
            product = Product.objects.get(id=item['product'])
        except (KeyError, ObjectDoesNotExist):
            bad_key = item.get('product', None)
            return Response(
                {"products": f'Недопустимый первичный ключ "{bad_key}"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=int(item['quantity']),
            price=product.price,
        )

    return Response({'status': 'ok', 'order_id': order.id})