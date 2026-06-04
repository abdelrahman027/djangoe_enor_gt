
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ProductItem, ProductImage, ProductReview
from category.models import Category


def product_list(request):
    # ✅ Only active categories
    categories = Category.objects.filter(is_active=True).order_by('category_name')

    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            is_available=True,
            name__icontains=query
        ).select_related('category').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(color__isnull=True).order_by('id')[:1], to_attr='main_images'),
            Prefetch('items', queryset=ProductItem.objects.filter(is_active=True).order_by('price'), to_attr='active_items'),
            Prefetch('reviews', queryset=ProductReview.objects.filter(published=True), to_attr='published_reviews')
        ).order_by('-updated_at')
    else:
        # Filter products: only available + active category
        products = Product.objects.filter(
            is_available=True,
            category__is_active=True  # optional but safe
        ).select_related('category').prefetch_related('items', 'images').order_by('-created_at')
    
    # Get selected category
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        try:
            selected_category = categories.get(slug=category_slug)
            products = products.filter(category=selected_category)
        except Category.DoesNotExist:
            pass  # ignore invalid slug

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category')
        .prefetch_related(
            'items__color',
            'items__size',
            'items__style',
            'images',
            'reviews__user'
        ),
        slug=slug,
        is_available=True
    )

    # Get all active items (variants) with stock info
    items = product.items.filter(is_active=True).select_related('color', 'size', 'style')

    # Group images by color (optional enhancement)
    images_by_color = {}

    for image in ProductImage.objects.filter(product=product):
        color_id = image.color_id or 'default'
        if color_id not in images_by_color:
            images_by_color[color_id] = []
        images_by_color[color_id].append(image)

    # Fetch reviews (published only)
    reviews_count = ProductReview.objects.filter(published=True,product=product).count()
    reviews = ProductReview.objects.filter(published=True,product=product).select_related('user')[:5]

    context = {
        'product': product,
        'items': items,
        'images_by_color': images_by_color,
        'reviews': reviews,
        'reviews_count': reviews_count,
    }
    return render(request, 'product_detail.html', context)