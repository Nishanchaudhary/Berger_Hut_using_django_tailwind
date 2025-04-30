from .models import Order

def cart_context(request):
    context = {}
    if request.user.is_authenticated:
        pending_order = Order.objects.filter(
            user=request.user,
            status='pending'
        ).prefetch_related('items').first()
        context['cart_count'] = pending_order.items.count() if pending_order else 0
    else:
        context['cart_count'] = 0
    return context