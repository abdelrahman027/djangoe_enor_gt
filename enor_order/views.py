from django.shortcuts import render ,redirect , get_object_or_404
from enor_cart.models import CartItem,Cart
from .models import Voucher,VoucherUsage,Order,OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from enor_profile.models import UserAddress
from django.db.models import F
from enor_store.models import ProductItem



def checkout_view(request):
    user_addresses = request.user.addresses.filter(user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    sub_total= cart.get_subtotal()
    total= cart.get_total()
    
    context = {
        'user_addresses': user_addresses,
        'total': total,
        'sub_total': sub_total,
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'checkout.html',context=context)


@login_required
def apply_voucher(request):
    code = request.POST.get('code')

    try:
        voucher = Voucher.objects.get(code__iexact=code)
    except Voucher.DoesNotExist:
        messages.error(request, "Invalid voucher code")
        return redirect('cart_detail')

    cart = request.user.cart
    cart_total = cart.get_total()

    if not voucher.is_valid(cart_total):
        messages.error(request, "Voucher is not valid")
        return redirect('cart_detail')

    if VoucherUsage.objects.filter(user=request.user, voucher=voucher).exists():
        messages.error(request, "You already used this voucher")
        return redirect('cart_detail')

    cart.voucher = voucher
    cart.save()

    messages.success(request, "Voucher applied successfully")
    return redirect('cart_detail')

@login_required
def remove_voucher(request):
    cart = request.user.cart
    if cart.voucher:
        cart.voucher = None
        cart.save()
        messages.success(request, "Voucher removed successfully")
    else:
        messages.info(request, "No voucher to remove")
    return redirect('cart_detail')





@transaction.atomic
def create_order_from_cart(cart, payment_method="cod", instapay_payment_id=None, address_id=None):

    if not cart.items.exists():
        raise ValueError("Cannot create order from empty cart")
    PAYMENT_METHODS = ["cod","instapay"]
    if payment_method not in PAYMENT_METHODS :
        raise ValueError("Invalid payment method")

    address = get_object_or_404(
        UserAddress,
        id=address_id,
        user=cart.user
    )

    subtotal = cart.get_subtotal()
    discount = cart.get_discount()
    total = subtotal - discount

    order = Order.objects.create(
        user=cart.user,
        voucher=cart.voucher,
        subtotal=subtotal,
        discount=discount,
        total=total,
        address=address,
        payment_method=payment_method,
        instapay_payment_id=instapay_payment_id,
    )

    for item in cart.items.select_related('product_item'):
        OrderItem.objects.create(
            order=order,
            product_item=item.product_item,
            price=item.product_item.price,
            quantity=item.quantity
        )
        ProductItem.objects.filter(
        pk=item.product_item.pk,
        stock_quantity__gte=item.quantity
    ).update(
        stock_quantity=F('stock_quantity') - item.quantity
    )


    if cart.voucher:
        VoucherUsage.objects.create(user=cart.user, voucher=cart.voucher)
        Voucher.objects.filter(pk=cart.voucher.pk).update(
            used_count=F('used_count') + 1
        )

    cart.items.all().delete()
    cart.voucher = None
    cart.save(update_fields=['voucher'])

    return order

@login_required
def order_place(request):
    if request.method != "POST":
        return redirect('order_placeholder')
    payment_method = request.POST.get('payment_method')
    address_id = request.POST.get('address_id')
    instapay_payment_id=request.POST.get("instapay_payment_id")
    if payment_method == "instapay" :
        if not instapay_payment_id :
            messages.error(request,"please add instapay reference number")
            return redirect("order_placeholder")
    try:
        order = create_order_from_cart(
            cart=request.user.cart,
            payment_method=payment_method,
            address_id=address_id,
            instapay_payment_id=instapay_payment_id,
        )
    except Exception as e:
        messages.error(request, str(e))
        print("error ",e)
        return redirect('order_placeholder')

    return redirect('order_confirmation', order_id=order.id)

@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )
    return render(request, 'order_confirmation.html', {'order': order})


@login_required
def my_orders_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .select_related('voucher')
        .order_by('-created_at')
    )
    return render(request, 'orders_list.html', {'orders': orders})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order_items = order.items.select_related('product_item')

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items
    })