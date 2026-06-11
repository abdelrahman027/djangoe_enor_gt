from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Prefetch,F
from enor_core.utils import send_resend_email
from enor_store.models import Product,ProductImage,ProductItem,ProductReview


def home(request):
    # messages.info(request, "Welcome to Enor! Explore our latest products and offers.")
    # send_resend_email("Test Email", "noreply@enorfitness.com", "body24792@gmail.com", "<h1>Test Email</h1>")
    products = Product.objects.filter(
        is_available=True,
        before_price__gt=F('base_price')
    ).select_related('category').prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(color__isnull=True).order_by('id')[:1], to_attr='main_images'),
        Prefetch('items', queryset=ProductItem.objects.filter(is_active=True).order_by('price'), to_attr='active_items'),
        Prefetch('reviews', queryset=ProductReview.objects.filter(published=True), to_attr='published_reviews')
    ).order_by('-updated_at')
    features = [
    {
      "icon": "<svg xmlns='http://www.w3.org/2000/svg' width='68' height='68' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' class='lucide lucide-zap-icon lucide-zap'><path d='M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z'/></svg>",
      "title": "Fast Shipping",
      "desc": "Fast And Affordable Shipping",
    },
    {
      "icon": "<svg xmlns='http://www.w3.org/2000/svg' width='68' height='68' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' class='lucide lucide-shield-check-icon lucide-shield-check'><path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/></svg>",
      "title": "Secure Checkout",
      "desc": "Only Trusted payments No cards required",
    },
    { "icon": "<svg xmlns='http://www.w3.org/2000/svg' width='68' height='68' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' class='lucide lucide-refresh-cw-icon lucide-refresh-cw'><path d='M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8'/><path d='M21 3v5h-5'/><path d='M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16'/><path d='M3 21v-5h5'/></svg>", "title": "Easy access", "desc": "Access your products anytime, anywhere" },
  ]
    return render(request,"index.html",{"products":products,"features":features})


def about_view(request):
    return render(request,"about.html")


def privacy_view(request):
    return render(request,"privacy.html")


def terms_service(request):
    return render(request,"terms_of_service.html")



def hot_deals(request):
    # Only products on sale: before_price > base_price AND is_available
    sale_products = Product.objects.filter(
        is_available=True,
        before_price__gt=F('base_price')
    ).select_related('category').prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(color__isnull=True).order_by('id')[:1], to_attr='main_images'),
        Prefetch('items', queryset=ProductItem.objects.filter(is_active=True).order_by('price'), to_attr='active_items'),
        Prefetch('reviews', queryset=ProductReview.objects.filter(published=True), to_attr='published_reviews')
    ).order_by('-updated_at')

    # Annotate count for efficiency (optional)
    # But for small sets, len() is fine in template

    return render(request, 'hot_deals.html', {
        'sale_products': sale_products,
    })



def search_view(request):
    query = request.GET.get('q', '')
    if query:
        results = Product.objects.filter(
            is_available=True,
            name__icontains=query
        ).select_related('category').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(color__isnull=True).order_by('id')[:1], to_attr='main_images'),
            Prefetch('items', queryset=ProductItem.objects.filter(is_active=True).order_by('price'), to_attr='active_items'),
            Prefetch('reviews', queryset=ProductReview.objects.filter(published=True), to_attr='published_reviews')
        ).order_by('-updated_at')
    else:
        results = Product.objects.all()
    return render(request,"product_list.html",{"results":results})