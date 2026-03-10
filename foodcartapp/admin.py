from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .services import get_sorted_restaurants

from .models import Product, ProductCategory, ProductCategory, Restaurant, RestaurantMenuItem, Order, OrderItem


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = (
        'id', 'status',
        'firstname', 'lastname',
        'phonenumber', 'address', 'payment_method',
        'comment', 'created_at', 'called_at',
        'nearest_restaurant', 'delivered_at'
    )
    list_editable = ['status', 'payment_method']
    search_fields = ('firstname', 'lastname', 'phonenumber', 'address')
    list_filter   = ('created_at',)
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]


    def nearest_restaurant(self, obj):
        sorted_restaurants = get_sorted_restaurants(obj.address)
        if not sorted_restaurants:
            return "Нет данных"
        rest, dist = sorted_restaurants[0]
        return f"{rest.name} — {dist} км"


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, OrderItem) and obj.price is None:
                obj.price = obj.product.price
            obj.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()


    def redirect_back(self, request):
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return None


    def response_change(self, request, obj):
        resp = super().response_change(request, obj)
        back = self.redirect_back(request)
        
        return back or resp


    def response_add(self, request, obj, post_url_continue=None):
        resp = super().response_add(request, obj, post_url_continue)
        back = self.redirect_back(request)
        return back or resp