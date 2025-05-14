from django.urls import path
# import ویوهای فانکشنال از همین اپ
from . import views

app_name = 'employees' # نام اپ برای جلوگیری از تداخل نام‌ها

urlpatterns = [
    # مسیرهای مدیریت کارمندان (Employee)
    path('', views.employee_list, name='employee_list'), # لیست کارمندان
    path('create/', views.employee_create, name='employee_create'), # ایجاد کارمند جدید
    path('<int:pk>/', views.employee_detail, name='employee_detail'), # جزئیات کارمند
    path('<int:pk>/update/', views.employee_update, name='employee_update'), # ویرایش کارمند
    # path('<int:pk>/delete/', views.employee_delete, name='employee_delete'), # در صورت وجود ویو حذف

    # مسیرهای مدیریت حساب بانکی (BankAccount) - مرتبط با کارمند
    # مسیر ایجاد حساب بانکی جدید برای یک کارمند خاص
    path('<int:employee_id>/bank-account/create/', views.bank_account_create, name='bank_account_create'),
    # توجه: مسیرهای لیست، ویرایش و حذف برای BankAccount نیز باید اضافه شوند.
    # مثال: path('<int:employee_id>/bank-accounts/', views.bank_account_list, name='bank_account_list'),
    # مثال: path('bank-accounts/<int:pk>/update/', views.bank_account_update, name='bank_account_update'),
    # مثال: path('bank-accounts/<int:pk>/delete/', views.bank_account_delete, name='bank_account_delete'),

    # مسیرهای مربوط به سازمان‌ها و عضویت‌ها به اپ organizations منتقل شده‌اند و باید از اینجا حذف شوند.
    # path('organizations/', views.organization_list, name='organization_list'), # مثال: حذف شود
    # path('organizations/create/', views.organization_create, name='organization_create'), # مثال: حذف شود
    # ... سایر مسیرهای مربوط به سازمان‌ها و عضویت‌ها ...
]
