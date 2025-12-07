from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import distance

geolocator = Nominatim(user_agent="starburger")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def fetch_coordinates(address):
    location = geocode(address)
    if not location:
        return None, None
    return location.latitude, location.longitude


def get_distance_km(point1, point2):
    if not point1 or not point2:
        return None
    return round(distance(point1, point2).km, 2)


def get_sorted_restaurants(order_address):
    from .models import Restaurant

    order_coords = fetch_coordinates(order_address)

    if not order_coords or None in order_coords:
        print(f"[WARN] Невозможно вычислить координаты адреса: {order_address}")
        return []

    results = []

    for restaurant in Restaurant.objects.exclude(latitude__isnull=True, longitude__isnull=True):
        rest_coords = (restaurant.latitude, restaurant.longitude)

        if None in rest_coords:
            continue

        dist = get_distance_km(order_coords, rest_coords)
        results.append((restaurant, dist))

    return sorted(results, key=lambda r: r[1])
