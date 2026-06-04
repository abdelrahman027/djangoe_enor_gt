from django.contrib import admin
from .models import (
    Product,
    ProductItem,
    Color,
    Size,
    Style,ProductReview ,ProductImage
)
# Register your models here.
class ProductItemInline(admin.TabularInline):
    model = ProductItem
    extra = 1
    readonly_fields = ('sku',)
    autocomplete_fields = ('color', 'size', 'style')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'is_available',
        'is_featured',
        'created_at'
    )

    list_filter = (
        'is_available',
        'is_featured',
        'category'
    )

    search_fields = (
        'name',
        'description'
    )

    prepopulated_fields = {'slug': ('name',)}

    inlines = [ProductItemInline]
    
@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'product',
        'color',
        'size',
        'style',
        'price',
        'stock_quantity',
        'is_active'
    )

    list_filter = (
        'product',
        'color',
        'size',
        'style',
        'is_active'
    )

    search_fields = (
        'sku',
        'product__name'
    )

    readonly_fields = ('sku',)

    autocomplete_fields = (
        'product',
        'color',
        'size',
        'style'
    )
    
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code',)
    search_fields = ('name',)
    
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
    
@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'published', 'created_at')
    list_filter = ('published', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    autocomplete_fields = ('product', 'user')
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'alt_text')
    search_fields = ('product__name', 'alt_text')
    autocomplete_fields = ('product', 'color')