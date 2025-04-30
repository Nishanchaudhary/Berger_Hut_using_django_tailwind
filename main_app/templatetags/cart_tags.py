from django import template
from ..models import Order

register = template.Library()

@register.simple_tag
def get_cart_count(user):
    if user.is_authenticated:
        order = Order.objects.filter(
            user=user,
            status='pending'
        ).prefetch_related('items').first()
        return order.items.count() if order else 0
    return 0