from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from .models import Product, Order, OrderItem

from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    order = Order.objects.create(
        firstname=request_data['firstname'],
        lastname=request_data['lastname'],
        phonenumber=request_data['phonenumber'],
        address=request_data['address'],
    )
    for item in request_data['products']:
        product = get_object_or_404(Product, id=item['product'])
        OrderItem.objects.create(
            order=order, product=product,
            quantity=int(item['quantity']),
            price=product.price,
        )
    return Response({'status': 'ok', 'order_id': order.id})