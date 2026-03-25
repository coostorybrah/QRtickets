from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def vnd(value):
    """Format a number like 300.000 đ."""
    try:
        number = int(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError):
        return value

    sign = '-' if number < 0 else ''
    grouped = f"{abs(number):,}".replace(',', '.')
    return f"{sign}{grouped} đ"
