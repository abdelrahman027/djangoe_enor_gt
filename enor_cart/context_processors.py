from enor_cart.models import Cart
from django.db.models import Sum
def cart_count(request):
    if not request.user.is_authenticated:
        return {'cart_items_count': 0}

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return {'cart_items_count': 0}

    cart_items_count = (
        cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    )

    return {'cart_items_count': cart_items_count}