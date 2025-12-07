from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from .models import Address

geolocator = Nominatim(user_agent="starburger")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_or_create_coordinates(address_text):
    address_obj, created = Address.objects.get_or_create(query=address_text)

    if address_obj.latitude and address_obj.longitude:
        return (address_obj.latitude, address_obj.longitude)

    location = geocode(address_text)
    if location:
        address_obj.latitude = location.latitude
        address_obj.longitude = location.longitude
        address_obj.save()

        return (location.latitude, location.longitude)

    return None
