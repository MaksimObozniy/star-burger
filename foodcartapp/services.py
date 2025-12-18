from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import distance
from geocoder.services import get_or_create_coordinates


geolocator = Nominatim(user_agent="starburger")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def get_distance_km(point1, point2):
    if not point1 or not point2:
        return None
    
    return round(distance(point1, point2).km, 2)


def get_sorted_restaurants(order_address):
    from .models import Restaurant

    order_coords = get_or_create_coordinates(order_address)
    if not order_coords:
        return None

    results = []

    for restaurant in Restaurant.objects.exclude(latitude__isnull=True):
        rest_coords = (restaurant.latitude, restaurant.longitude)
        dist = distance(order_coords, rest_coords).km
        results.append((restaurant, round(dist, 2)))

    return sorted(results, key=lambda r: r[1])
