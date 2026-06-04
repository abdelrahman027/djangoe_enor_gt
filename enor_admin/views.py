
from django.shortcuts import render,redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from enor_store.models import Product, Color, Size, Style, ProductItem, ProductImage ,ProductReview
from enor_content.models import FAQ,Contact_us,Social_links,Newsletter
from enor_order.models import Order,Voucher
from enor_profile.models import UserProfile
from django.core.paginator import Paginator
from category.models import Category
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q ,F
from enor_order.models import OrderItem as OrderItemModel
from decimal import Decimal
from django.contrib.auth.models import User
@admin_required(roles=['Admin', 'Editor'])
def admin_dashboard(request):
    # Stats
    total_products = Product.objects.count()
    total_variants = ProductItem.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_users = UserProfile.objects.count()
    active_users = UserProfile.objects.filter(status='Active').count()
    total_vouchers = Voucher.objects.count()

    # Recent items
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    recent_products = Product.objects.order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_variants': total_variants,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_users': total_users,
        'active_users': active_users,
        'total_vouchers': total_vouchers,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
    }
    return render(request, 'admin_home.html', context)


# ===== PRODUCT LIST =====
@admin_required(roles=['Admin', 'Editor'])
def admin_product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.select_related('category').prefetch_related(
        'items', 'images'
    ).order_by('-created_at')

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.filter(is_active=True)

    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'products/product_list.html', context)

# ===== PRODUCT CREATE =====
@admin_required(roles=['Admin', 'Editor'])
def admin_product_create(request):
    categories = Category.objects.filter(is_active=True)
    colors = Color.objects.all()
    sizes = Size.objects.all()
    styles = Style.objects.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # --- Create Product ---
                product = Product.objects.create(
                    name=request.POST.get('name', '').strip(),
                    category_id=request.POST.get('category'),
                    description=request.POST.get('description', ''),
                    base_price=request.POST.get('base_price', '0') or '0',
                    before_price=request.POST.get('before_price', '0') or '0',
                    is_available=request.POST.get('is_available') == 'on',
                    is_featured=request.POST.get('is_featured') == 'on',
                )

                # Main image
                if request.FILES.get('image'):
                    product.image = request.FILES['image']
                    product.save()

                # --- Create Variants ---
                colors_list = request.POST.getlist('variant_color[]')
                sizes_list = request.POST.getlist('variant_size[]')
                styles_list = request.POST.getlist('variant_style[]')
                prices_list = request.POST.getlist('variant_price[]')
                stocks_list = request.POST.getlist('variant_stock[]')

                for i in range(len(prices_list)):
                    price = prices_list[i].strip()
                    if not price:
                        continue
                    ProductItem.objects.create(
                        product=product,
                        color_id=colors_list[i] or None,
                        size_id=sizes_list[i] or None,
                        style_id=styles_list[i] or None,
                        price=price,
                        stock_quantity=stocks_list[i] or '0',
                        is_active=True
                    )

                # --- Create Images ---
                files = request.FILES.getlist('new_image[]')
                color_ids = request.POST.getlist('new_image_color[]')
                alts = request.POST.getlist('new_image_alt[]')

                for i, file in enumerate(files):
                    if not file:
                        continue
                    ProductImage.objects.create(
                        product=product,
                        image=file,
                        color_id=color_ids[i] if i < len(color_ids) else None,
                        alt_text=(alts[i].strip() if i < len(alts) else '') or product.name
                    )

                messages.success(request, f"✅ Product '{product.name}' created!")
                return redirect('admin_product_list')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    return render(request, 'products/product_form.html', {
        'categories': categories,
        'colors': colors,
        'sizes': sizes,
        'styles': styles,
    })


# ===== PRODUCT EDIT =====
@admin_required(roles=['Admin', 'Editor'])
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.filter(is_active=True)
    colors = Color.objects.all()
    sizes = Size.objects.all()
    styles = Style.objects.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # --- Update Product ---
                product.name = request.POST.get('name', '').strip()
                product.category_id = request.POST.get('category')
                product.description = request.POST.get('description', '')
                product.base_price = request.POST.get('base_price', '0') or '0'
                product.before_price = request.POST.get('before_price', '0') or '0'
                product.is_available = request.POST.get('is_available') == 'on'
                product.is_featured = request.POST.get('is_featured') == 'on'

                if request.FILES.get('image'):
                    product.image = request.FILES['image']
                product.save()

                # --- Update Images ---
                # Update existing
                for img in product.images.all():
                    img_id = str(img.id)
                    new_file = request.FILES.get(f'existing_image_file_{img_id}')
                    new_color_id = request.POST.get(f'existing_image_color_{img_id}')
                    new_alt = request.POST.get(f'existing_image_alt_{img_id}', '').strip()

                    if new_file:
                        img.image = new_file
                    img.color_id = new_color_id or None
                    img.alt_text = new_alt or product.name
                    img.save()

                # Add new
                files = request.FILES.getlist('new_image[]')
                color_ids = request.POST.getlist('new_image_color[]')
                alts = request.POST.getlist('new_image_alt[]')

                for i, file in enumerate(files):
                    if not file:
                        continue
                    ProductImage.objects.create(
                        product=product,
                        image=file,
                        color_id=color_ids[i] if i < len(color_ids) else None,
                        alt_text=(alts[i].strip() if i < len(alts) else '') or product.name
                    )

                # --- Update Variants (SAFE) ---
                ids = request.POST.getlist('variant_id[]')
                colors_list = request.POST.getlist('variant_color[]')
                sizes_list = request.POST.getlist('variant_size[]')
                styles_list = request.POST.getlist('variant_style[]')
                prices_list = request.POST.getlist('variant_price[]')
                stocks_list = request.POST.getlist('variant_stock[]')

                submitted_ids = set()

                for i in range(len(prices_list)):
                    price = prices_list[i].strip()
                    if not price:
                        continue

                    item_id = ids[i] if i < len(ids) else None
                    color_id = colors_list[i] or None
                    size_id = sizes_list[i] or None
                    style_id = styles_list[i] or None
                    stock = stocks_list[i] or '0'

                    if item_id and item_id.isdigit():
                        # Update existing
                        try:
                            item = ProductItem.objects.get(id=item_id, product=product)
                            
                            # 🔒 If in orders, only update price/stock (preserve identity)
                            if item.order_items.exists():  # ← uses your SET_NULL + related_name
                                item.price = price
                                item.stock_quantity = stock
                            else:
                                # Full update
                                item.color_id = color_id
                                item.size_id = size_id
                                item.style_id = style_id
                                item.price = price
                                item.stock_quantity = stock
                            
                            item.save()
                            submitted_ids.add(item.id)
                        except ProductItem.DoesNotExist:
                            pass
                    else:
                        # Create new
                        item = ProductItem.objects.create(
                            product=product,
                            color_id=color_id,
                            size_id=size_id,
                            style_id=style_id,
                            price=price,
                            stock_quantity=stock,
                            is_active=True
                        )
                        submitted_ids.add(item.id)

                # Archive unused variants (soft delete)
                ProductItem.objects.filter(
                    product=product
                ).exclude(
                    id__in=submitted_ids
                ).update(is_active=False)

                messages.success(request, f"✅ Product '{product.name}' updated!")
                return redirect('admin_product_list')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    # Prepare variants for template (only active ones)
    variants_data = []
    for item in product.items.filter(is_active=True):
        variants_data.append({
            'id': item.id,
            'color_id': item.color_id,
            'size_id': item.size_id,
            'style_id': item.style_id,
            'price': item.price,
            'stock': item.stock_quantity,
            'in_orders': item.order_items.exists(),  # ← works with SET_NULL + related_name='order_items'
        })

    return render(request, 'products/product_form.html', {
        'product': product,
        'categories': categories,
        'colors': colors,
        'sizes': sizes,
        'styles': styles,
        'variants_data': variants_data,
    })
# ===== PRODUCT DELETE =====
@admin_required(roles=['Admin', 'Editor'])
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"🗑️ Product '{name}' deleted.")
        return redirect('admin_product_list')

    context = {'product': product}
    return render(request, 'products/product_confirm_delete.html', context)

# ====== PRODUCT DETAIL ======

@admin_required(roles=['Admin', 'Editor'])
def admin_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Stats
    order_items = OrderItemModel.objects.filter(
        product_item__product=product
    ).select_related('order', 'product_item')
    
    total_order_count = order_items.count()
    total_revenue = order_items.aggregate(
        total=Sum('price', field='price * quantity')
    )['total'] or 0

    recent_orders = order_items.order_by('-order__created_at')[:5]
    reviews = ProductReview.objects.filter(
        product=product, published=True
    ).select_related('user').order_by('-created_at')
    review_count = reviews.count()

    context = {
        'product': product,
        'active_variants_count': product.items.filter(is_active=True).count(),
        'total_order_count': total_order_count,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'reviews': reviews,
        'review_count': review_count,
    }
    return render(request, 'products/product_detail.html', context)


# ===== ORDER LIST =====
@admin_required(roles=['Admin', 'Editor'])
def admin_order_list(request):
    # Filters
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_query = request.GET.get('user', '')

    orders = Order.objects.select_related(
        'user', 'voucher', 'address'
    ).prefetch_related(
        'items__product_item__product'
    ).order_by('-created_at')

    if status:
        orders = orders.filter(status=status)
    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)
    if user_query:
        orders = orders.filter(
            Q(user__username__icontains=user_query) |
            Q(user__email__icontains=user_query) |
            Q(user__profile__real_name__icontains=user_query)
        )

    # Pagination
    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'page_obj': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'current_filters': {
            'status': status,
            'start_date': start_date,
            'end_date': end_date,
            'user': user_query,
        },
    }
    return render(request, 'orders/order_list.html', context)


# ===== ORDER DETAIL =====
@admin_required(roles=['Admin', 'Editor'])
def admin_order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related(
            'user', 'user__profile', 'voucher', 'address'
        ).prefetch_related(
            'items__product_item__product'
        ),
        id=order_id
    )

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/order_detail.html', context)


# ===== UPDATE ORDER STATUS =====
@admin_required(roles=['Admin', 'Editor'])
def admin_order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # 🔒 Basic validation: ensure it's a valid choice
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, "❌ Invalid status.")
            return redirect('admin_order_detail', order_id=order.id)

        # Optional: Add business logic (e.g., prevent reverting 'completed')
        # For simplicity, we allow any change (you can tighten later)
        old_status = order.status
        order.status = new_status
        order.save()

        if old_status != new_status:
            messages.success(request, f"✅ Status updated from '{order.get_status_display}' to '{order.get_status_display}'.")
        else:
            messages.info(request, "ℹ️ Status unchanged.")

    return redirect('admin_order_detail', order_id=order.id)


# ===== VOUCHER LIST =====
@admin_required(roles=['Admin'])
def admin_voucher_list(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')

    vouchers = Voucher.objects.all().order_by('-valid_from')

    if query:
        vouchers = vouchers.filter(code__icontains=query)
    if status == 'active':
        now = timezone.now()
        vouchers = vouchers.filter(
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
            used_count__lt=F('usage_limit')
        )
    elif status == 'inactive':
        now = timezone.now()
        vouchers = vouchers.exclude(
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
            used_count__lt=F('usage_limit')
        )

    # Annotate usage
    for voucher in vouchers:
        voucher.is_valid_now = voucher.is_valid(Decimal('0'))  # dummy total

    context = {
        'vouchers': vouchers,
        'query': query,
        'status': status,
    }
    return render(request, 'vouchers/voucher_list.html', context)


# ===== VOUCHER CREATE =====
@admin_required(roles=['Admin'])
def admin_voucher_create(request):
    if request.method == 'POST':
        try:
            code = request.POST.get('code', '').strip().upper()
            if not code:
                messages.error(request, "❌ Voucher code is required.")
                return render(request, 'vouchers/voucher_form.html')

            if Voucher.objects.filter(code=code).exists():
                messages.error(request, "❌ Voucher code already exists.")
                return render(request, 'vouchers/voucher_form.html')

            voucher = Voucher.objects.create(
                code=code,
                discount_type=request.POST.get('discount_type'),
                discount_value=request.POST.get('discount_value'),
                min_order_amount=request.POST.get('min_order_amount', '0') or '0',
                valid_from=request.POST.get('valid_from'),
                valid_to=request.POST.get('valid_to'),
                usage_limit=request.POST.get('usage_limit', '1') or '1',
                is_active=request.POST.get('is_active') == 'on'
            )

            messages.success(request, f"✅ Voucher '{voucher.code}' created!")
            return redirect('admin_voucher_list')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    return render(request, 'vouchers/voucher_form.html')


# ===== VOUCHER EDIT =====
@admin_required(roles=['Admin'])
def admin_voucher_edit(request, voucher_id):
    voucher = get_object_or_404(Voucher, id=voucher_id)

    if request.method == 'POST':
        try:
            code = request.POST.get('code', '').strip().upper()
            if not code:
                messages.error(request, "❌ Voucher code is required.")
                return render(request, 'vouchers/voucher_form.html', {'voucher': voucher})

            # Allow same code (self), but no duplicates
            if Voucher.objects.filter(code=code).exclude(id=voucher.id).exists():
                messages.error(request, "❌ Voucher code already exists.")
                return render(request, 'vouchers/voucher_form.html', {'voucher': voucher})

            voucher.code = code
            voucher.discount_type = request.POST.get('discount_type')
            voucher.discount_value = request.POST.get('discount_value')
            voucher.min_order_amount = request.POST.get('min_order_amount', '0') or '0'
            voucher.valid_from = request.POST.get('valid_from')
            voucher.valid_to = request.POST.get('valid_to')
            voucher.usage_limit = request.POST.get('usage_limit', '1') or '1'
            voucher.is_active = request.POST.get('is_active') == 'on'
            voucher.save()

            messages.success(request, f"✅ Voucher '{voucher.code}' updated!")
            return redirect('admin_voucher_list')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    return render(request, 'vouchers/voucher_form.html', {'voucher': voucher})


# ===== VOUCHER DELETE =====
@admin_required(roles=['Admin'])
def admin_voucher_delete(request, voucher_id):
    voucher = get_object_or_404(Voucher, id=voucher_id)
    
    if request.method == 'POST':
        code = voucher.code
        voucher.delete()
        messages.success(request, f"🗑️ Voucher '{code}' deleted.")
        return redirect('admin_voucher_list')

    context = {'voucher': voucher}
    return render(request, 'vouchers/voucher_confirm_delete.html', context)


# ===== USER LIST =====
@admin_required(roles=['Admin'])
def admin_user_list(request):
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    users = User.objects.select_related('profile').order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__real_name__icontains=query)
        )
    if role:
        users = users.filter(profile__role=role)
    if status:
        users = users.filter(profile__status=status)

    # Annotate stats
    for user in users:
        user.order_count = user.orders.count()
        user.address_count = user.addresses.count()

    context = {
        'users': users,
        'query': query,
        'role_filter': role,
        'status_filter': status,
        'role_choices': UserProfile.user_roles,
        'status_choices': UserProfile.status_choices,
    }
    return render(request, 'users/user_list.html', context)


# ===== USER DETAIL =====
@admin_required(roles=['Admin'])
def admin_user_detail(request, user_id):
    user = get_object_or_404(
        User.objects.select_related('profile')
        .prefetch_related(
            'addresses',
            'orders__items__product_item__product'
        ),
        id=user_id
    )

    orders = user.orders.select_related('voucher').order_by('-created_at')[:5]
    addresses = user.addresses.all()

    context = {
        'user': user,
        'orders': orders,
        'addresses': addresses,
        'role_choices': UserProfile.user_roles,
        'status_choices': UserProfile.status_choices,
    }
    return render(request, 'users/user_detail.html', context)


# ===== USER EDIT =====
@admin_required(roles=['Admin'])
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            # Update User
            user.email = request.POST.get('email', '').strip()
            user.save()

            # Update UserProfile
            profile = user.profile
            profile.real_name = request.POST.get('real_name', '').strip()
            profile.email = request.POST.get('profile_email', '').strip()
            profile.main_phone = request.POST.get('main_phone', '').strip()
            profile.secondary_phone = request.POST.get('secondary_phone', '').strip()
            profile.role = request.POST.get('role')
            profile.status = request.POST.get('status')
            
            # Handle avatar
            if request.FILES.get('image'):
                profile.image = request.FILES['image']
            
            profile.save()

            messages.success(request, f"✅ User '{user.username}' updated!")
            return redirect('admin_user_detail', user_id=user.id)

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    context = {
        'user': user,
        'role_choices': UserProfile.user_roles,
        'status_choices': UserProfile.status_choices,
    }
    return render(request, 'users/user_form.html', context)



# enor_admin/views.py



# ===== FAQ LIST =====
@admin_required(roles=['Admin'])
def admin_faq_list(request):
    faqs = FAQ.objects.all()
    
    if request.method == 'POST':
        for faq in faqs:
            faq.order = request.POST.get(f'order_{faq.id}', 0)
            faq.is_active = request.POST.get(f'active_{faq.id}') == 'on'
            faq.save()
        messages.success(request, "✅ FAQs updated!")
        return redirect('admin_faq_list')

    context = {'faqs': faqs}
    return render(request, 'settings/faq_list.html', context)


# ===== FAQ CREATE =====
@admin_required(roles=['Admin'])
def admin_faq_create(request):
    if request.method == 'POST':
        try:
            FAQ.objects.create(
                question=request.POST.get('question', '').strip(),
                answer=request.POST.get('answer', '').strip(),
                order=request.POST.get('order', 0),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, "✅ FAQ added!")
            return redirect('admin_faq_list')
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
    
    return render(request, 'settings/faq_form.html')


# ===== FAQ EDIT =====
@admin_required(roles=['Admin'])
def admin_faq_edit(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        try:
            faq.question = request.POST.get('question', '').strip()
            faq.answer = request.POST.get('answer', '').strip()
            faq.order = request.POST.get('order', 0)
            faq.is_active = request.POST.get('is_active') == 'on'
            faq.save()
            messages.success(request, "✅ FAQ updated!")
            return redirect('admin_faq_list')
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
    
    context = {'faq': faq}
    return render(request, 'settings/faq_form.html')


# ===== FAQ DELETE =====
@admin_required(roles=['Admin'])
def admin_faq_delete(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        question = faq.question[:30]
        faq.delete()
        messages.success(request, f"🗑️ FAQ '{question}...' deleted.")
        return redirect('admin_faq_list')
    return render(request, 'settings/faq_confirm_delete.html', {'faq': faq})


# ===== CONTACT MESSAGES =====
@admin_required(roles=['Admin'])
def admin_contact_list(request):
    contacts = Contact_us.objects.all().order_by('-submitted_at')
    context = {'contacts': contacts}
    return render(request, 'settings/contact_list.html', context)


# ===== SOCIAL LINKS =====
@admin_required(roles=['Admin'])
def admin_social_list(request):
    socials = Social_links.objects.all()
    
    if request.method == 'POST':
        for social in socials:
            social.order = request.POST.get(f'order_{social.id}', 0)
            social.is_active = request.POST.get(f'active_{social.id}') == 'on'
            social.save()
        messages.success(request, "✅ Social links updated!")
        return redirect('admin_social_list')

    context = {'socials': socials}
    return render(request, 'settings/social_list.html', context)


# ===== SOCIAL CREATE =====
@admin_required(roles=['Admin'])
def admin_social_create(request):
    if request.method == 'POST':
        try:
            Social_links.objects.create(
                name=request.POST.get('name', '').strip(),
                link=request.POST.get('link', '').strip(),
                icon=request.POST.get('icon', '').strip(),
                order=request.POST.get('order', 0),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, "✅ Social link added!")
            return redirect('admin_social_list')
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
    
    return render(request, 'settings/social_form.html')


# ===== SOCIAL EDIT =====
@admin_required(roles=['Admin'])
def admin_social_edit(request, social_id):
    social = get_object_or_404(Social_links, id=social_id)
    
    if request.method == 'POST':
        try:
            social.name = request.POST.get('name', '').strip()
            social.link = request.POST.get('link', '').strip()
            social.icon = request.POST.get('icon', '').strip()
            social.order = request.POST.get('order', 0)
            social.is_active = request.POST.get('is_active') == 'on'
            social.save()
            messages.success(request, "✅ Social link updated!")
            return redirect('admin_social_list')
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
    
    context = {'social': social}
    return render(request, 'settings/social_form.html',context)


# ===== NEWSLETTER =====
@admin_required(roles=['Admin'])
def admin_newsletter_list(request):
    query = request.GET.get('q', '')
    newsletters = Newsletter.objects.all().order_by('-subscribed_at')
    
    if query:
        newsletters = newsletters.filter(email__icontains=query)
    
    # For export
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Subscribed At'])
        for n in newsletters:
            writer.writerow([n.email, n.subscribed_at])
        return response

    context = {
        'newsletters': newsletters,
        'query': query,
        'total': Newsletter.objects.count(),
    }
    return render(request, 'settings/newsletter_list.html', context)




@admin_required(roles=['Admin','Editor'])
def admin_privacy_policy_setting(request):
    return render(request, 'pages/privacy_policy_setting.html')



@admin_required(roles=['Admin','Editor'])
def admin_terms_and_conditions_setting(request):
    return render(request, 'pages/terms_and_conditions_setting.html')



@admin_required(roles=['Admin','Editor'])
def admin_shipping_policy_setting(request):
    return render(request, 'pages/shipping_policy_setting.html')