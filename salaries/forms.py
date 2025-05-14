from django import forms
from .models import SalaryItemType, EmployeeSalaryItem
from django.utils.translation import gettext_lazy as _

# Import necessary models from other apps if needed for form fields (e.g., ForeignKey choices)
from organizations.models import Organization
from employees.models import Employee
from settings_app.models import FinancialPeriod


class SalaryItemTypeForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش انواع آیتم‌های حقوقی (SalaryItemType).
    """
    class Meta:
        model = SalaryItemType
        fields = [
            'organization',
            'financial_period',
            'name',
            'item_type',
            'is_base_salary',
            'is_deduction',
        ]
        labels = { # برچسب‌های فارسی
            'organization': _('سازمان'),
            'financial_period': _('دوره مالی'),
            'name': _('نام آیتم حقوقی'),
            'item_type': _('نوع محاسبه'),
            'is_base_salary': _('جز حقوق پایه است؟'),
            'is_deduction': _('کسر از حقوق است؟'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'financial_period': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'is_base_salary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_deduction': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        # می‌توانید اعتبارسنجی‌های اضافی را در متدهای clean_* اضافه کنید


class EmployeeSalaryItemForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش آیتم‌های حقوقی کارمند (EmployeeSalaryItem).
    """
    class Meta:
        model = EmployeeSalaryItem
        fields = [
            'employee',
            'financial_period',
            'salary_item_type',
            'amount',
        ]
        labels = { # برچسب‌های فارسی
            'employee': _('کارمند'),
            'financial_period': _('دوره مالی'),
            'salary_item_type': _('نوع آیتم حقوقی'),
            'amount': _('مبلغ'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'financial_period': forms.Select(attrs={'class': 'form-control'}),
            'salary_item_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}), # یا forms.TextInput بسته به نیاز
        }
        # اعتبارسنجی منحصر به فرد بودن در مدل انجام می‌شود.

    # Example: You might want to filter the choices for financial_period or salary_item_type
    # based on the selected organization or employee in the view.
    # This would require overriding the __init__ method.
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Example: Filter financial periods by organization if organization is available
    #     # if 'organization_pk' in self.initial:
    #     #     org_pk = self.initial['organization_pk']
    #     #     self.fields['financial_period'].queryset = FinancialPeriod.objects.filter(organization__pk=org_pk)
    #     # Example: Filter salary item types by financial period and organization
    #     # if 'financial_period_pk' in self.initial and 'organization_pk' in self.initial:
    #     #     period_pk = self.initial['financial_period_pk']
    #     #     org_pk = self.initial['organization_pk']
    #     #     self.fields['salary_item_type'].queryset = SalaryItemType.objects.filter(
    #     #         financial_period__pk=period_pk, organization__pk=org_pk
    #     #     )
