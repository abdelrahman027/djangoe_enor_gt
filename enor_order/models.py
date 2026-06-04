from django.db import models
from django.contrib.auth.models import User
from enor_store.models import ProductItem
from enor_profile.models import UserAddress
import uuid

# vouchers/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal

class Voucher(models.Model):
    DISCOUNT_TYPE = (
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def is_valid(self, cart_total):
        now = timezone.now()

        if not self.is_active:
            return False

        if self.valid_from > now or self.valid_to < now:
            return False

        if self.used_count >= self.usage_limit:
            return False

        if cart_total < self.min_order_amount:
            return False

        return True

    def apply_discount(self, cart_total):
        if self.discount_type == 'percent':
            return cart_total * (self.discount_value / 100)
        return min(self.discount_value, cart_total)

    def __str__(self):
        return self.code
    
class VoucherUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'voucher')
        
        
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('deliverd', 'Deliverd'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    address=models.ForeignKey(UserAddress,on_delete=models.SET_NULL,null=True,blank=True)

    voucher = models.ForeignKey(
        Voucher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(max_length=50, default='cod')
    instapay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    product_item = models.ForeignKey(
        ProductItem,
        on_delete=models.SET_NULL,related_name='order_items',null=True ,blank=True
    )
        # Frozen at order time — never change
    product_name = models.CharField(max_length=255,blank=True)
    variant_name = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def get_total(self):
        return self.price * self.quantity
    def save(self, *args, **kwargs):
        # Only populate on creation (not updates)
        if not self.pk and self.product_item:
            item = self.product_item
            
            # Product name
            self.product_name = item.product.name if item.product else "Unknown Product"
            
            # Variant description
            parts = []
            if item.color:
                parts.append(item.color.name)
            if item.size:
                parts.append(item.size.name)
            if item.style:
                parts.append(item.style.name)
            self.variant_name = " / ".join(parts) or "Default"
            
            # SKU
            self.sku = item.sku or f"ORDER-{self.order.id}-ITEM-{self.id}"
        
        # Safety fallback
        if not self.product_name:
            self.product_name = "Deleted item"
            self.variant_name = ""
            self.sku = ""
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} × {self.product_name} ({self.variant_name})"