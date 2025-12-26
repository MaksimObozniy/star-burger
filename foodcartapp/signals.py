from django.db.models.signals import post_save
from django.dispatch import receiver

from foodcartapp.models import Restaurant
from geocoder.services import get_or_create_coordinates


@receiver(post_save, sender=Restaurant)
def fill_restaurant_coordinates(sender, instance, **kwargs):
    if not instance.address:
        return

    get_or_create_coordinates(instance.address)
