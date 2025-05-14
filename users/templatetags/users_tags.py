from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Allows accessing dictionary items by key in Django templates.
    Example: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key)

# You can add other custom filters or simple tags here as well.
