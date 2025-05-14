# employees/templatetags/custom_filters.py

from django import template

# یک نمونه از Library ایجاد می‌کنیم تا تگ‌ها و فیلترهای سفارشی خود را در آن ثبت کنیم
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    فیلتری برای دسترسی به یک آیتم از دیکشنری با استفاده از کلید.
    مثال استفاده در تمپلیت: {{ my_dict|get_item:my_key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    try:
        # تلاش برای دسترسی به آیتم با استفاده از کلید (برای QueryDict و موارد مشابه)
        return dictionary[key]
    except (KeyError, TypeError):
        # اگر کلید یافت نشد یا شیء قابل دسترسی با کلید نیست
        return None

# می‌توانید فیلترها یا تگ‌های سفارشی دیگری را نیز در اینجا اضافه کنید.
