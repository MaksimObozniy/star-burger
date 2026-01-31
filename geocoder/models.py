from django.db import models

class Place(models.Model):
    address = models.CharField(max_length=255, unique=True, verbose_name='Адресс')
    latitude = models.FloatField(null=True, blank=True, verbose_name="Ширина")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
    
    def __str__(self):
        return self.address