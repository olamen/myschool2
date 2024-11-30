# accounting/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def paid_status(value):
    return "Payé" if value else "Non Payé"