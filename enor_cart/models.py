from django.db import models
from django.contrib.auth.models import User
from enor_store.models import ProductItem
from enor_order.models import Voucher
from decimal import Decimal
# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(  # ✔ one active cart per user
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    voucher = models.ForeignKey(
        Voucher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_subtotal(self):
        return sum(
            (item.product_item.price * item.quantity for item in self.items.all()),
            Decimal('0.00')
        )

    def get_discount(self):
        subtotal = self.get_subtotal()

        if self.voucher and self.voucher.is_valid(subtotal):
            return self.voucher.apply_discount(subtotal)

        return Decimal('0.00')

    def get_total(self):
        subtotal = self.get_subtotal()
        discount = self.get_discount()

        # auto-remove invalid voucher
        if self.voucher and discount == 0:
            self.voucher = None
            self.save(update_fields=['voucher'])

        return subtotal - discount

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product_item.product.name} in cart {self.cart.id}"
    
    def get_total_price(self):
        return self.product_item.price * self.quantity
    class Meta:
        unique_together = ('cart', 'product_item')