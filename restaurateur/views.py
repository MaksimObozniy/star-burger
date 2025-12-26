from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from geocoder.models import Place
from geopy.distance import distance

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
        .with_total_price()
        .order_by('-id')
        .with_available_restaurants()
    )

    order_addresses = {o.address for o in orders if o.address}

    restaurant_addresses = set()
    for o in orders:
        for r in getattr(o, 'available_restaurants', []):
            if r.address:
                restaurant_addresses.add(r.address)

    all_addresses = order_addresses | restaurant_addresses

    places_by_address = {
        p.address: p
        for p in Place.objects.filter(address__in=all_addresses)
    }

    order_items = []

    for order in orders:
        total_cost = order.total_price

        if order.restaurant:
            order_items.append({
                'order': order,
                'restaurants': [{'restaurant': order.restaurant, 'distance_km': None}],
                'address_not_found': False,
                'total_cost': total_cost,
            })
            continue

        order_place = places_by_address.get(order.address)
        if not order_place or order_place.latitude is None or order_place.longitude is None:
            order_items.append({
                'order': order,
                'restaurants': [],
                'address_not_found': True,
                'total_cost': total_cost,
            })
            continue

        order_coords = (order_place.latitude, order_place.longitude)

        restaurants_with_distance = []
        for restaurant in getattr(order, 'available_restaurants', []):
            restaurant_place = places_by_address.get(restaurant.address)
            if not restaurant_place or restaurant_place.latitude is None or restaurant_place.longitude is None:
                continue

            rest_coords = (restaurant_place.latitude, restaurant_place.longitude)
            dist_km = round(distance(order_coords, rest_coords).km, 2)

            restaurants_with_distance.append({
                'restaurant': restaurant,
                'distance_km': dist_km,
            })

        restaurants_with_distance.sort(key=lambda x: x['distance_km'])

        order_items.append({
            'order': order,
            'restaurants': restaurants_with_distance,
            'address_not_found': False,
            'total_cost': total_cost,
        })

    return render(request, 'order_items.html', {'order_items': order_items})