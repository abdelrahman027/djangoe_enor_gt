from django.shortcuts import render,redirect , get_object_or_404

from enor_admin.decorators import admin_required

from django.contrib import messages


#categoryadmin views 


from enor_store.models import Category as CategoryModel

# ===== CATEGORY LIST =====
@admin_required(roles=['Admin', 'Editor'])
def admin_category_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    categories = CategoryModel.objects.all().order_by('-created_at')

    if query:
        categories = categories.filter(category_name__icontains=query)
    if status_filter == 'active':
        categories = categories.filter(is_active=True)
    elif status_filter == 'inactive':
        categories = categories.filter(is_active=False)

    # Usage stats
    for cat in categories:
        cat.product_count = cat.products.filter(is_available=True).count()

    context = {
        'categories': categories,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'category/category_list.html', context)


# ===== CATEGORY CREATE =====
@admin_required(roles=['Admin', 'Editor'])
def admin_category_create(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('category_name', '').strip()
            if not name:
                messages.error(request, "❌ Category name is required.")
                return render(request, 'category/category_form.html')

            # Check uniqueness (case-insensitive)
            if CategoryModel.objects.filter(category_name__iexact=name).exists():
                messages.error(request, "❌ A category with this name already exists.")
                return render(request, 'category/category_form.html')

            category = CategoryModel.objects.create(
                category_name=name,
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on'
            )

            # Handle image
            if request.FILES.get('cat_image'):
                category.cat_image = request.FILES['cat_image']
                category.save()

            messages.success(request, f"✅ Category '{category.category_name}' created!")
            return redirect('admin_category_list')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    return render(request, 'category/category_form.html')


# ===== CATEGORY EDIT =====
@admin_required(roles=['Admin', 'Editor'])
def admin_category_edit(request, category_id):
    category = get_object_or_404(CategoryModel, id=category_id)

    if request.method == 'POST':
        try:
            name = request.POST.get('category_name', '').strip()
            if not name:
                messages.error(request, "❌ Category name is required.")
                return render(request, 'category/category_form.html', {'category': category})

            # Check uniqueness (excluding self)
            if CategoryModel.objects.filter(category_name__iexact=name).exclude(id=category.id).exists():
                messages.error(request, "❌ A category with this name already exists.")
                return render(request, 'category/category_form.html', {'category': category})

            category.category_name = name
            category.description = request.POST.get('description', '')
            category.is_active = request.POST.get('is_active') == 'on'

            if request.FILES.get('cat_image'):
                category.cat_image = request.FILES['cat_image']
            category.save()

            messages.success(request, f"✅ Category '{category.category_name}' updated!")
            return redirect('admin_category_list')

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    return render(request, 'category/category_form.html', {'category': category})


# ===== CATEGORY DELETE =====
@admin_required(roles=['Admin'])
def admin_category_delete(request, category_id):
    category = get_object_or_404(CategoryModel, id=category_id)
    
    # Check if used in products
    active_products = category.products.filter(is_available=True).count()
    inactive_products = category.products.filter(is_available=False).count()
    
    if request.method == 'POST':
        if active_products > 0:
            messages.error(request, "❌ Cannot delete: category has active products.")
            return redirect('admin_category_detail', category_id=category.id)
        
        name = category.category_name
        category.delete()
        messages.success(request, f"🗑️ Category '{name}' deleted.")
        return redirect('admin_category_list')

    context = {
        'category': category,
        'active_products': active_products,
        'inactive_products': inactive_products,
    }
    return render(request, 'category/category_confirm_delete.html', context)


# ===== CATEGORY DETAIL (Optional but Recommended) =====
@admin_required(roles=['Admin', 'Editor'])
def admin_category_detail(request, category_id):
    category = get_object_or_404(CategoryModel, id=category_id)
    products = category.products.select_related('category').prefetch_related('images').order_by('-created_at')
    active_products = category.products.filter(is_available=True)
    print(active_products)
    
    context = {
        'category': category,
        'products': products,
        'product_count': products.count(),
        'active_products':active_products
    }
    return render(request, 'category/category_detail.html', context)