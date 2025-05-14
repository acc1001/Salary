"""
URL configuration for your_project_name project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # برای مدیریت فایل‌های مدیا در حالت توسعه
from django.conf.urls.static import static # برای مدیریت فایل‌های مدیا در حالت توسعه

# فرض می‌کنیم شما یک ویو برای صفحه اصلی دارید، مثلاً در یک اپلیکیشن core یا مستقیماً اینجا
# اگر صفحه اصلی شما یک تمپلیت ساده است، می‌توانید از TemplateView استفاده کنید.
from django.views.generic import TemplateView

urlpatterns = [
    # مسیر پنل ادمین جنگو
    path('admin/', admin.site.urls),

    # مسیر صفحه اصلی پروژه
    # فرض می‌کنیم تمپلیت home.html در مسیر templates/home.html یا templates/your_app_name/home.html قرار دارد.
    # اگر از TemplateView استفاده می‌کنید:
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # اگر ویوی فانکشنال یا کلاس بیس دارید:
    # path('', views.home_view, name='home'), # مثال: اگر ویوی home_view در views.py اصلی دارید

    # شامل کردن مسیرهای URL اپلیکیشن users (احراز هویت، مدیریت کاربران و دسترسی‌ها)
    # اطمینان حاصل کنید که app_name = 'users' در users/urls.py تنظیم شده است.
    path('users/', include('users.urls')),

    # شامل کردن مسیرهای URL اپلیکیشن organizations (مدیریت سازمان‌ها و عضویت‌ها)
    # اطمینان حاصل کنید که app_name = 'organizations' در organizations/urls.py تنظیم شده است.
    path('organizations/', include('organizations.urls')),

    # شامل کردن مسیرهای URL اپلیکیشن employees (مدیریت کارمندان و حساب‌های بانکی)
    # اطمینان حاصل کنید که app_name = 'employees' در employees/urls.py تنظیم شده است.
    path('employees/', include('employees.urls')),

    # شامل کردن مسیرهای URL اپلیکیشن hr (منابع انسانی: دپارتمان‌ها، عناوین شغلی، سوابق شغلی، کارکرد)
    # اطمینان حاصل کنید که app_name = 'hr' در hr/urls.py تنظیم شده است.
    path('hr/', include('hr.urls')),

    # شامل کردن مسیرهای URL اپلیکیشن settings_app (تنظیمات مالی و سازمانی)
    # اطمینان حاصل کنید که app_name = 'settings_app' در settings_app/urls.py تنظیم شده است.
    path('settings/', include('settings_app.urls')), # یا هر مسیر دیگری که برای تنظیمات در نظر گرفته‌اید

    # شامل کردن مسیرهای URL اپلیکیشن loans (مدیریت وام‌های کارکنان)
    # اطمینان حاصل کنید که app_name = 'loans' در loans/urls.py تنظیم شده است.
    path('loans/', include('loans.urls')),

    # شامل کردن مسیرهای URL اپلیکیشن salaries (محاسبات حقوق و دستمزد)
    # اطمینان حاصل کنید که app_name = 'salaries' در salaries/urls.py تنظیم شده است.
    path('salaries/', include('salaries.urls')),

    # اضافه کردن مسیرهای فایل‌های مدیا در حالت توسعه (DEBUG=True)
    # این خطوط فقط در محیط توسعه برای سرو کردن فایل‌های آپلود شده (مانند عکس پرسنلی) لازم هستند.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# می‌توانید مسیرهای فایل‌های استاتیک را نیز در حالت توسعه اضافه کنید (اگر collectstatic استفاده نمی‌کنید)
# اما توصیه می‌شود در محیط پروداکشن از وب سرور برای سرو استاتیک‌ها استفاده کنید.
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

