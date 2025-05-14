from django import forms
# import مدل‌های باقی‌مانده در اپ employees
from .models import Employee, BankAccount # EmployeeOrganization و Organization حذف شده‌اند

# اگر فرم‌ها به مدل‌های سازمان نیاز دارند، آنها را از organizations.models وارد کنید
from organizations.models import Organization, EmployeeOrganization # <--- import از اپ organizations
from django.utils.translation import gettext_lazy as _ # برای استفاده از ترجمه در label ها


# import فرم احراز هویت از اینجا حذف شده و باید در اپ users باشد.
# from django.contrib.auth.forms import AuthenticationForm

class EmployeeForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات کارمند.
    """
    # می‌توانید ویجت‌های خاصی برای فیلدها تعریف کنید
    # photo = forms.ImageField(label="تصویر پرسنلی", required=False, widget=forms.FileInput)
    # birth_date = forms.DateField(label="تاریخ تولد", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Employee
        # فیلد user_account معمولاً در فرم نمایش داده نمی‌شود و در ویو تنظیم می‌گردد، بنابراین آن را exclude می‌کنیم.
        # فیلدهایی که در مدل Employee فعلی شما وجود ندارند (مانند employee_number, marital_status, number_of_children) حذف شده‌اند.
        fields = [
            'national_code',
            'first_name',
            'last_name',
            'photo', # نیاز به وجود فیلد photo در مدل Employee
            'date_of_birth', # نام فیلد در مدل Employee فعلی 'date_of_birth' است
            'hire_date', # اضافه کردن فیلدهای مهم مدل Employee
            'fire_date',
            'is_active',
        ]
        # اگر فیلد user_account را در فرم نمی‌خواهید، از exclude استفاده کنید
        exclude = ['user_account'] # <--- اطمینان از exclude شدن user_account
        labels = { # تعریف برچسب‌های فارسی برای فیلدها در فرم
            'national_code': _("کد ملی"),
            'first_name': _("نام"),
            'last_name': _("نام خانوادگی"),
            'photo': _("تصویر پرسنلی"),
            'date_of_birth': _("تاریخ تولد"),
            'hire_date': _("تاریخ استخدام"),
            'fire_date': _("تاریخ پایان همکاری"),
            'is_active': _("فعال"),
        }
        widgets = { # تعریف ویجت‌های خاص برای نمایش بهتر
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # 'marital_status': forms.Select(attrs={'class': 'form-control'}),
            # 'organizations': forms.CheckboxSelectMultiple # یا forms.SelectMultiple بسته به نیاز UI
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        # می‌توانید اعتبارسنجی‌های اضافی را در متدهای clean_* اضافه کنید


class BankAccountForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات حساب بانکی.
    """
    class Meta:
        model = BankAccount
        fields = [
            'bank_name', # نام فیلد در مدل BankAccount فعلی 'bank_name' است
            'account_number',
            'sheba_number', # نام فیلد در مدل BankAccount فعلی 'sheba_number' است
            'card_number',
            # 'bank_branch', # این فیلد در مدل BankAccount فعلی شما وجود ندارد
            'is_active',
            # 'employee', # فیلد employee معمولاً در فرم مدل حساب بانکی نمایش داده نمی‌شود و در ویو تنظیم می‌گردد
        ]
        exclude = ['employee'] # <--- اطمینان از exclude شدن employee
        labels = {
            'bank_name': _("نام بانک"),
            'account_number': _("شماره حساب"),
            'sheba_number': _("شماره شبا"),
            'card_number': _("شماره کارت"),
            # 'bank_branch': _("نام شعبه"),
            'is_active': _("فعال"),
        }
        widgets = { # اضافه کردن کلاس بوت استرپ به ویجت‌ها
             'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
             'account_number': forms.TextInput(attrs={'class': 'form-control'}),
             'sheba_number': forms.TextInput(attrs={'class': 'form-control'}),
             'card_number': forms.TextInput(attrs={'class': 'form-control'}),
            # 'bank_branch': forms.TextInput(attrs={'class': 'form-control'}),
             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# توجه: فرم EmployeeOrganizationForm به اپ organizations منتقل شده است.
# اگر نیاز به فرمی برای EmployeeOrganization دارید، باید آن را در organizations/forms.py تعریف کنید.
# class EmployeeOrganizationForm(forms.ModelForm):
#     """
#     فرم مدل برای مدیریت عضویت کارمند در سازمان.
#     """
#     class Meta:
#         model = EmployeeOrganization # این مدل در اپ organizations است
#         fields = '__all__'
#         labels = {
#             'employee': _("کارمند"),
#             'organization': _("سازمان"),
#             'start_date': _("تاریخ شروع همکاری"),
#             'end_date': _("تاریخ پایان همکاری"),
#         }
#         widgets = { # اضافه کردن کلاس بوت استرپ به ویجت‌ها
#              'employee': forms.Select(attrs={'class': 'form-control'}),
#              'organization': forms.Select(attrs={'class': 'form-control'}),
#              'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#              'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#         }


# فرم CustomLoginForm از اینجا حذف شده و به اپ users منتقل می‌شود.
