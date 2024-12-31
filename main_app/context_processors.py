# context_processors.py
from .models import OrderItem, Order

def cart_item_count(request):
    if request.user.is_authenticated:
        # Assuming you have a way to identify the current order
        current_order = Order.objects.filter(user=request.user, is_completed=False).first()
        if current_order:
            total_items = sum(item.quantity for item in current_order.items.all())
            return {'cart_item_count': total_items}
    return {'cart_item_count': 0}
