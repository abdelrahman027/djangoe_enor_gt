from decimal import Decimal
from django.db import models

class Shipping(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    @property
    def get_amount(self):
        return self.amount if self.amount else Decimal('100.00')
    
    def __str__(self):
        return f"Shipping: {self.get_amount()}"
