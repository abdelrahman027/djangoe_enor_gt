from django.urls import path
from . import views
from category import views as categoryViews



urlpatterns = [
path("theboss",views.admin_dashboard,name="theboss"),
path('products/', views.admin_product_list, name='admin_product_list'),
path('products/create/', views.admin_product_create, name='admin_product_create'),
path('products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
path('products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
path('products/<int:product_id>/', views.admin_product_detail, name='admin_product_detail'),

#category

path('categories/', categoryViews.admin_category_list, name='admin_category_list'),
path('categories/create/', categoryViews.admin_category_create, name='admin_category_create'),
path('categories/<int:category_id>/edit/', categoryViews.admin_category_edit, name='admin_category_edit'),
path('categories/<int:category_id>/delete/', categoryViews.admin_category_delete, name='admin_category_delete'),
path('categories/<int:category_id>/', categoryViews.admin_category_detail, name='admin_category_detail'),

#orders

path('orders/', views.admin_order_list, name='admin_order_list'),
path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
path('orders/<int:order_id>/update-status/', views.admin_order_update_status, name='admin_order_update_status'),

#vouchers

path('vouchers/', views.admin_voucher_list, name='admin_voucher_list'),
path('vouchers/create/', views.admin_voucher_create, name='admin_voucher_create'),
path('vouchers/<int:voucher_id>/edit/', views.admin_voucher_edit, name='admin_voucher_edit'),
path('vouchers/<int:voucher_id>/delete/', views.admin_voucher_delete, name='admin_voucher_delete'),

# Users (Admin only)
path('users/', views.admin_user_list, name='admin_user_list'),
path('users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
path('users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),

# Settings & Content
path('settings/faqs/', views.admin_faq_list, name='admin_faq_list'),
path('settings/faqs/create/', views.admin_faq_create, name='admin_faq_create'),
path('settings/faqs/<int:faq_id>/edit/', views.admin_faq_edit, name='admin_faq_edit'),
path('settings/faqs/<int:faq_id>/delete/', views.admin_faq_delete, name='admin_faq_delete'),

path('settings/contacts/', views.admin_contact_list, name='admin_contact_list'),

path('settings/social/', views.admin_social_list, name='admin_social_list'),
path('settings/social/create/', views.admin_social_create, name='admin_social_create'),
path('settings/social/<int:social_id>/edit/', views.admin_social_edit, name='admin_social_edit'),

path('settings/newsletter/', views.admin_newsletter_list, name='admin_newsletter_list'),


# Colors
path('attributes/colors/', views.admin_color_list, name='admin_color_list'),
path('attributes/colors/create/', views.admin_color_create, name='admin_color_create'),
path('attributes/co lors/<int:color_id>/edit/', views.admin_color_edit, name='admin_color_edit'),
path('attributes/colors/<int:color_id>/delete/', views.admin_color_delete, name='admin_color_delete'),

# Sizes
path('attributes/sizes/', views.admin_size_list, name='admin_size_list'),
path('attributes/sizes/create/', views.admin_size_create, name='admin_size_create'),
path('attributes/sizes/<int:size_id>/edit/', views.admin_size_edit, name='admin_size_edit'),
path('attributes/sizes/<int:size_id>/delete/', views.admin_size_delete, name='admin_size_delete'),

# Styles
path('attributes/styles/', views.admin_style_list, name='admin_style_list'),
path('attributes/styles/create/', views.admin_style_create, name='admin_style_create'),
path('attributes/styles/<int:style_id>/edit/', views.admin_style_edit, name='admin_style_edit'),
path('attributes/styles/<int:style_id>/delete/', views.admin_style_delete, name='admin_style_delete'),

]