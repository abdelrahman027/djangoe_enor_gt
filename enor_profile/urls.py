from django.urls import path
from . import views



urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('address/add/', views.address_add_view, name='address_add'),
    path('address/edit/<int:address_id>/', views.address_edit_view, name='address_edit'),
    path('address/delete/<int:address_id>/', views.address_delete_view, name='address_delete'),
]