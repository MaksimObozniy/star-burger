from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from .models import Place

geolocator = Nominatim(user_agent="starburger")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_or_create_coordinates(address_text):
    place, _ = Place.objects.get_or_create(address=address_text)

    if place.latitude and place.longitude:
        return (place.latitude, place.longitude)

    location = geocode(address_text)
    if not location:
        return None
    

    place.latitude = location.latitude
    place.longitude = location.longitude
    place.save()

    return (location.latitude, location.longitude)

