from django.contrib import admin
from .models import  Voucher,VoucherUsage,Order,OrderItem

# Register your models here.
admin.site.register(Voucher)
admin.site.register(VoucherUsage)
admin.site.register(Order)
admin.site.register(OrderItem)