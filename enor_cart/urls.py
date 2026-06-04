# cart/urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('add/', views.add_cart_item, name='add_cart_item'),
    path('', views.cart_detail, name='cart_detail'),
    path('add_qty/<int:item_id>/', views.cart_add_qty, name='cart_add_qty'),
    path('subtract_qty/<int:item_id>/', views.cart_subtract_qty, name='cart_subtract_qty'),
    
    path('remove_item/<int:item_id>/', views.cart_remove_item, name='cart_remove_item'),
    

]