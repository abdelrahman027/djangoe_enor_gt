from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'created_at'
    )

    search_fields = (
        'user__username',
        'user__email'
    )
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'cart',
        'product_item',
        'quantity'
    )

    search_fields = (
        'cart__user__username',
        'product_item__product__name',
        'product_item__sku'
    )