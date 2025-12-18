from django.db.models.signals import post_save
from django.dispatch import receiver

from geocoder.services import get_or_create_coordinates
from .models import Restaurant

@receiver(post_save, sender=Restaurant)
def fill_restauran_coordinates(sender, instance, created, **kwargs):
     
     if not instance.address:
         return
     
     if instance.latitude is not None and instance.longitude is not None:
         return
     
     coords = get_or_create_coordinates(instance.addresse)
     if not coords:
         return
     
     Restaurant.objects.filter(pk=instance.pk).update(
         latitude=coords[0],
         logitud=coords[1],
     )