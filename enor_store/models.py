from django.db import models
from category.models import Category
from django.utils.text import slugify
import uuid

from django.contrib.auth.models import User
class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/products', blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2 ,default=0)
    before_price = models.DecimalField(max_digits=10, decimal_places=2 ,default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
         base_slug = slugify(self.name)
         self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
        
    @property
    def average_rating(self):
        reviews = self.reviews.filter(published=True)
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return total_rating / reviews.count()
        return 0
    
    @property
    def is_on_sale(self):
        return self.before_price > self.base_price
    @property
    def discount_percentage(self):
        if self.before_price > self.base_price:
            return ((self.before_price - self.base_price) / self.before_price) * 100
        return 0

    @property
    def best_deal_item(self):
        """Returns the cheapest *in-stock* item, or cheapest overall if all out-of-stock."""
        in_stock = self.items.filter(is_active=True, stock_quantity__gt=0)
        if in_stock.exists():
            return in_stock.order_by('price').first()
        # fallback: cheapest item even if OOS
        return self.items.filter(is_active=True).order_by('price').first()

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7)  # e.g. #FFFFFF

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Style(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
    
class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True, blank=True)

    sku = models.CharField(max_length=100, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'color', 'size', 'style')
    indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product']),
        ]
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def image_url(self):
        image = ProductImage.objects.filter(product=self.product, color=self.color).first()
        if image:
            return image.image.url
        return None
    @property
    def is_in_orders(self):
        return self.order_items.exists()
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def generate_sku(self):
        parts = [
            slugify(self.product.name)[:10].upper(),
            self.color.name[:3].upper() if self.color else 'NA',
            self.size.name.upper() if self.size else 'NA',
            self.style.name[:3].upper() if self.style else 'STD',
        ]
        unique_part = uuid.uuid4().hex[:6].upper()
        return "-".join(parts + [unique_part])

    def __str__(self):
        return self.sku
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/product_images')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    alt_text = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
    
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    published = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.product.name} by {self.user.username}"
    

    