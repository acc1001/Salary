from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _ # برای ترجمه label ها


class CustomUser(AbstractUser):
    """
    مدل کاربری سفارشی که از AbstractUser جنگو ارث‌بری می‌کند.
    این مدل پایه و اساس سیستم احراز هویت پروژه است.
    در صورت نیاز به اضافه کردن فیلدهای جدید برای کاربران، اینجا اضافه می‌شوند.
    """
    # فیلدهای پیش‌فرض AbstractUser شامل:
    # username, first_name, last_name, email, is_staff, is_active,
    # date_joined, last_login, groups, user_permissions

    # اضافه کردن related_name برای جلوگیری از تداخل با مدل User پیش‌فرض جنگو
    # این کار زمانی لازم است که AUTH_USER_MODEL را تنظیم می‌کنید و ممکن است
    # اپ‌های دیگری در پروژه (مثل admin پیش‌فرض) به مدل User پیش‌فرض اشاره کنند.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'), # استفاده از ترجمه
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set", # related_name اختصاصی
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'), # استفاده از ترجمه
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_permissions", # related_name اختصاصی
        related_query_name="customuser",
    )

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.username

# نکته مهم:
# پس از تعریف این مدل CustomUser و قبل از اولین migration،
# باید در فایل settings.py پروژه، خط زیر را اضافه یا به‌روزرسانی کنید:
# AUTH_USER_MODEL = 'users.CustomUser'
# دقت کنید که این تنظیم فقط قبل از ایجاد جداول کاربری قابل تغییر است.
# اگر پروژه شما قبلاً با مدل User پیش‌فرض migrate شده،
# انتقال به CustomUser نیازمند مراحل پیچیده‌تری برای مهاجرت داده‌ها است.