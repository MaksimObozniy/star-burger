from django.db import models
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from .services import fetch_coordinates

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    latitude = models.FloatField(
        'широта',
        null=True,
        blank=True
    )
    longitude = models.FloatField(
        'долгота',
        null=True,
        blank=True
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if (self.latitude is None or self.longitude is None) and self.address:
            lat, lon = fetch_coordinates(self.address)
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=500,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuertSet(models.QuerySet):
    def with_total_price(self):
        line_total = ExpressionWrapper(
            F('items__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
        return self.annotate(total_price=Sum(line_total))


class Order(models.Model):
    class Status(models.TextChoices):
        UNPROCESSED = 'unprocessed', 'Необработанный'
        IN_PROCESSED = 'in_progress', 'Готовится'
        DELIVERED = 'delivered', 'Доставлен'

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        ELECTRONIC = 'electronic', 'Электронно'

    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Телефон', region='RU', db_index=True)
    address = models.CharField('Адрес', max_length=200)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='Способ оплаты'
    )

    created_at = models.DateTimeField('Создан', auto_now_add=True, db_index=True)
    called_at = models.DateTimeField('Дата звонка клиенту',null=True, blank=True )
    delivered_at = models.DateTimeField('Дата доставки',null=True, blank=True )
    
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPROCESSED,
        verbose_name='Статус',
        db_index=True
    )

    restaurant= models.ForeignKey(
        'Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ресторан-исполнитель',
        related_name='orders'
    )

    objects = OrderQuertSet.as_manager()
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='товар'
    )
    quantity = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True
        )
    
    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказа'

