from django import forms
# import مدل‌ها
from .models import FiscalYear, InsuranceCeiling, TaxLevel, FinancialPeriod
from django.utils.translation import gettext_lazy as _ # برای استفاده از ترجمه در label ها


class FiscalYearForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات سال مالی.
    """
    class Meta:
        model = FiscalYear
        # شامل فیلد organization اگر در فرم نمایش داده می‌شود، در غیر این صورت exclude شود
        fields = ['organization', 'title', 'start_date', 'end_date']
        labels = { # برچسب‌های فارسی
            'organization': _('سازمان'),
            'title': _('عنوان سال مالی'),
            'start_date': _('تاریخ شروع'),
            'end_date': _('تاریخ پایان'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ و نوع مناسب
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        # می‌توانید اعتبارسنجی‌های اضافی را در متدهای clean_* اضافه کنید
        # اعتبارسنجی همپوشانی تاریخ‌ها در متد clean() مدل انجام می‌شود.


class InsuranceCeilingForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات سقف بیمه.
    فیلد fiscal_year معمولاً در فرم نمایش داده نمی‌شود و در ویو تنظیم می‌گردد.
    """
    class Meta:
        model = InsuranceCeiling
        # فیلد fiscal_year در ویو تنظیم می‌شود، بنابراین در فرم نمایش داده نمی‌شود
        fields = ['amount']
        # یا exclude = ['fiscal_year']
        labels = { # برچسب فارسی
            'amount': _('مبلغ سقف بیمه'),
        }
        widgets = { # ویجت با کلاس بوت استرپ
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        # اعتبارسنجی منحصر به فرد بودن در مدل انجام می‌شود.


class TaxLevelForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات سطح مالیاتی.
    فیلد fiscal_year معمولاً در فرم نمایش داده نمی‌شود و در ویو تنظیم می‌گردد.
    """
    class Meta:
        model = TaxLevel
        # فیلد fiscal_year در ویو تنظیم می‌شود، بنابراین در فرم نمایش داده نمی‌شود
        fields = ['level_title', 'from_amount', 'to_amount', 'tax_percent']
        # یا exclude = ['fiscal_year']
        labels = { # برچسب‌های فارسی
            'level_title': _('عنوان سطح مالیاتی'),
            'from_amount': _('از مبلغ'),
            'to_amount': _('تا مبلغ'),
            'tax_percent': _('درصد مالیات'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'level_title': forms.TextInput(attrs={'class': 'form-control'}),
            'from_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'to_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_percent': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        # اعتبارسنجی همپوشانی بازه‌ها در متد clean() مدل انجام می‌شود.


class FinancialPeriodForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات دوره مالی.
    فیلد fiscal_year معمولاً در فرم نمایش داده نمی‌شود و در ویو تنظیم می‌گردد.
    """
    class Meta:
        model = FinancialPeriod
        # فیلد fiscal_year در ویو تنظیم می‌شود، بنابراین در فرم نمایش داده نمی‌شود
        fields = ['name', 'start_date', 'end_date', 'is_active'] # اضافه کردن is_active
        # یا exclude = ['fiscal_year']
        labels = { # برچسب‌های فارسی
            'name': _('نام دوره مالی'),
            'start_date': _('تاریخ شروع'),
            'end_date': _('تاریخ پایان'),
            'is_active': _('فعال بودن'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
             'name': forms.TextInput(attrs={'class': 'form-control'}),
             'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # ویجت مناسب برای BooleanField
        }
        # اعتبارسنجی همپوشانی تاریخ‌ها در متد clean() مدل انجام می‌شود.

    # تنظیمات دلخواه برای فیلدها (اختیاری - اگر در Meta widgets تعریف شوند، اینجا لزومی ندارد)
    # name = forms.CharField(max_length=100, label=_("نام دوره مالی"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    # start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label=_("تاریخ شروع"))
    # end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label=_("تاریخ پایان"))

