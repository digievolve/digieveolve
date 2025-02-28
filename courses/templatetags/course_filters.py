from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the argument"""
    return value * arg

@register.filter(name='divide')
def divide(value, arg):
    """Divide the value by the argument"""
    if arg == 0:
        return 0
    return value / arg