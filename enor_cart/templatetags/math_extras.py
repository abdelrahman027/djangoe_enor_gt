# cart/templatetags/math_extras.py
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply value by arg (for price * qty)"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0