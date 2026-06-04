from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Cart, CartItem
from enor_store.models import ProductItem
from urllib.parse import urlencode


@login_required
def add_cart_item(request):
    if request.method == 'POST':
        item_sku = request.POST.get('product_item_sku')
        product_item = get_object_or_404(ProductItem, sku=item_sku)
        query_string = urlencode({'item': product_item.sku})
        url = reverse('product_detail', kwargs={'slug': product_item.product.slug})
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_item=product_item,
            defaults={'quantity': 1}
        )
        messages.success(request, "✅ Item added to cart successfully!")
        if not created:
            messages.info(request, "ℹ️ Item already in cart, increased quantity by 1.")
            cart_item.quantity += 1
            cart_item.save()
            
        if query_string and url:
            return redirect(f"{url}?{query_string}")

    return redirect('product_detail', slug=product_item.product.slug)


def cart_detail(request):
    print(request.user.cart.get_subtotal())
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total= cart.get_total()
    sub_total= cart.get_subtotal()
    difference = sub_total - total
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'sub_total': sub_total,
        'difference': difference,
    }
    return render(request, 'cart_detail.html', context)

def cart_add_qty(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    if cart_item.quantity > cart_item.product_item.stock_quantity:
        messages.error(request, "❌ Sorry out of stock.")
        cart_item.quantity = cart_item.product_item.stock_quantity
    cart_item.save()
    return redirect('cart_detail')

def cart_subtract_qty(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        messages.error(request, "❌ Quantity cannot be less than 1. To remove the item, please use the remove option.")
    return redirect('cart_detail')


def cart_remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "✅ Item removed from cart.")
    return redirect('cart_detail')