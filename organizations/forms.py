from django import forms
from .models import Organization, EmployeeOrganization
from django.utils.translation import gettext_lazy as _ # برای استفاده از ترجمه در label ها

class OrganizationForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات سازمان.
    """
    class Meta:
        model = Organization
        fields = ['name', 'code', 'address', 'phone_number', 'email', 'website', 'is_active']
        labels = { # برچسب‌های فارسی
            'name': _('نام سازمان'),
            'code': _('کد سازمان'),
            'address': _('آدرس'),
            'phone_number': _('شماره تماس'),
            'email': _('ایمیل'),
            'website': _('وب‌سایت'),
            'is_active': _('فعال'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmployeeOrganizationForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش عضویت کارمند در سازمان.
    """
    class Meta:
        model = EmployeeOrganization
        # فیلدهای employee و organization معمولا در ویو یا بر اساس URL تنظیم می‌شوند،
        # اما اگر می‌خواهید در فرم انتخاب شوند، آن‌ها را در fields قرار دهید.
        # در اینجا فرض می‌کنیم که employee و organization در فرم انتخاب می‌شوند.
        fields = ['employee', 'organization', 'start_date', 'end_date', 'is_active']
        labels = { # برچسب‌های فارسی
            'employee': _('کارمند'),
            'organization': _('سازمان'),
            'start_date': _('تاریخ شروع عضویت'),
            'end_date': _('تاریخ پایان عضویت'),
            'is_active': _('عضویت فعال'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        # اعتبارسنجی همپوشانی بازه‌ها در متد clean() مدل انجام می‌شود.

