from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from geocoder.services import get_or_create_coordinates
from foodcartapp.services import get_distance_km

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = (
        Order.objects
        .exclude(status=Order.Status.DELIVERED)
        .select_related('restaurant')
        .prefetch_related('items__product')
        .order_by('-id')
    )

    order_items = []

    for order in orders:

        if order.restaurant:
            order_items.append({
                'order': order,
                'restaurants': [{
                    'restaurant': order.restaurant,
                    'distance_km': None,
                }],
                'address_not_found': False,
            })
            continue

        product_ids = order.items.values_list('product_id', flat=True)

        available_restaurants = (
            Restaurant.objects
            .filter(menu_items__product_id__in=product_ids)
            .distinct()
            .order_by('name')
        )

        order_coords = get_or_create_coordinates(order.address)

        if not order_coords:
            restaurants_with_distance = []
            address_not_found = True
        else:
            address_not_found = False
            restaurants_with_distance = []

            for restaurant in available_restaurants:
                if restaurant.latitude is None or restaurant.longitude is None:
                    continue

                dist_km = get_distance_km(order_coords, (restaurant.latitude, restaurant.longitude))
                restaurants_with_distance.append({
                    'restaurant': restaurant,
                    'distance_km': dist_km,
                })

            restaurants_with_distance.sort(key=lambda x: x['distance_km'] if x['distance_km'] is not None else 10**9)

        order_items.append({
            'order': order,
            'restaurants': restaurants_with_distance,
            'address_not_found': address_not_found,
        })

    return render(
        request,
        'order_items.html',
        {'order_items': order_items}
    )