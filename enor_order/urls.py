from django.urls import path
from . import views



urlpatterns = [
    # Placeholder for order-related URLs
    path('checkout/', views.checkout_view, name='order_placeholder'),
    path('order_confirmation/<order_id>', views.order_confirmation_view, name='order_confirmation'),
    # path('confirmation/<str:reference_number>/', views.order_confirmation, name='order_confirmation'),
    path('place/',views.order_place,name='place_order'),
    path('my_orders/',views.my_orders_view,name='user_orders'),
    path('order_details/<order_id>/',views.order_detail_view,name='order_detail'),
    path("apply_voucher/",views.apply_voucher,name="apply_voucher"),
    path("remove_voucher/",views.remove_voucher,name="remove_voucher"),
]
