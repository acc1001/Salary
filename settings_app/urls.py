from django.urls import path
# import ویوهای کلاس بیس از همین اپ
from .views import (
    FiscalYearListView,
    FiscalYearCreateView,
    FiscalYearUpdateView,
    # FiscalYearDeleteView, # در صورت اضافه کردن ویو حذف

    InsuranceCeilingListView,
    InsuranceCeilingCreateView,
    InsuranceCeilingUpdateView, # اضافه شده

    TaxLevelListView,
    TaxLevelCreateView,
    TaxLevelUpdateView, # اضافه شده

    FinancialPeriodListView,
    FinancialPeriodCreateView,
    FinancialPeriodUpdateView,
)

app_name = 'settings_app' # نام اپ برای جلوگیری از تداخل نام‌ها

urlpatterns = [
    # مسیرهای مدیریت سال‌های مالی (FiscalYear)
    path('fiscal-years/', FiscalYearListView.as_view(), name='fiscal_year_list'),
    path('fiscal-years/create/', FiscalYearCreateView.as_view(), name='fiscal_year_create'),
    path('fiscal-years/<int:pk>/update/', FiscalYearUpdateView.as_view(), name='fiscal_year_update'),
    # path('fiscal-years/<int:pk>/delete/', FiscalYearDeleteView.as_view(), name='fiscal_year_delete'),

    # مسیرهای مدیریت سقف‌های بیمه (InsuranceCeiling) - مرتبط با سال مالی
    # مسیر لیست سقف‌های بیمه برای یک سال مالی خاص
    path(
        'fiscal-years/<int:fiscal_year_pk>/insurance-ceilings/',
        InsuranceCeilingListView.as_view(),
        name='insurance_ceiling_list'
    ),
    # مسیر ایجاد سقف بیمه جدید برای یک سال مالی خاص
    path(
        'fiscal-years/<int:fiscal_year_pk>/insurance-ceilings/create/',
        InsuranceCeilingCreateView.as_view(),
        name='insurance_ceiling_create'
    ),
    # مسیر ویرایش سقف بیمه
    path(
        'insurance-ceilings/<int:pk>/update/', # pk مربوط به خود InsuranceCeiling است
        InsuranceCeilingUpdateView.as_view(),
        name='insurance_ceiling_update'
    ),
    # path('insurance-ceilings/<int:pk>/delete/', InsuranceCeilingDeleteView.as_view(), name='insurance_ceiling_delete'),


    # مسیرهای مدیریت سطوح مالیاتی (TaxLevel) - مرتبط با سال مالی
     # مسیر لیست سطوح مالیاتی برای یک سال مالی خاص
    path(
        'fiscal-years/<int:fiscal_year_pk>/tax-levels/',
        TaxLevelListView.as_view(),
        name='tax_level_list'
    ),
    # مسیر ایجاد سطح مالیاتی جدید برای یک سال مالی خاص
    path(
        'fiscal-years/<int:fiscal_year_pk>/tax-levels/create/',
        TaxLevelCreateView.as_view(),
        name='tax_level_create'
    ),
    # مسیر ویرایش سطح مالیاتی
    path(
        'tax-levels/<int:pk>/update/', # pk مربوط به خود TaxLevel است
        TaxLevelUpdateView.as_view(),
        name='tax_level_update'
    ),
    # path('tax-levels/<int:pk>/delete/', TaxLevelDeleteView.as_view(), name='tax_level_delete'),


    # مسیرهای مدیریت دوره‌های مالی (FinancialPeriod) - مرتبط با سال مالی
    # مسیر لیست دوره‌های مالی برای یک سال مالی خاص
     path(
        'fiscal-years/<int:fiscal_year_pk>/financial-periods/',
        FinancialPeriodListView.as_view(),
        name='financial_period_list'
    ),
     # مسیر ایجاد دوره مالی جدید برای یک سال مالی خاص
    path(
        'fiscal-years/<int:fiscal_year_pk>/financial-periods/create/',
        FinancialPeriodCreateView.as_view(),
        name='financial_period_create'
    ),
    # مسیر ویرایش دوره مالی
    path(
        'financial-periods/<int:pk>/update/', # pk مربوط به خود FinancialPeriod است
        FinancialPeriodUpdateView.as_view(),
        name='financial_period_update'
    ),
    # path('financial-periods/<int:pk>/delete/', FinancialPeriodDeleteView.as_view(), name='financial_period_delete'),

    # توجه: اگر نیاز به ویوهای جزئیات (DetailView) برای هر مدل دارید، باید مسیرهای مربوطه را نیز اضافه کنید.
    # مثال: path('fiscal-years/<int:pk>/', FiscalYearDetailView.as_view(), name='fiscal_year_detail'),
]
