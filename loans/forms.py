from django import forms
from django.utils.translation import gettext_lazy as _
from .models import EmployeeLoan

# Import models from other apps if needed for form fields (e.g., ForeignKey choices)
from employees.models import Employee
from organizations.models import Organization


class EmployeeLoanForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات وام کارمند.
    فیلتر کردن کارمندان بر اساس سازمان انتخاب شده.
    """
    class Meta:
        model = EmployeeLoan
        fields = [
            'employee',
            'organization',
            'loan_amount',
            'first_installment_date',
            'last_installment_date',
            'monthly_installment_amount',
            'is_settled',
        ]
        labels = {
            'employee': _('کارمند'),
            'organization': _('سازمان'),
            'loan_amount': _('مبلغ وام دریافتی'),
            'first_installment_date': _('تاریخ اولین قسط'),
            'last_installment_date': _('تاریخ آخرین قسط'),
            'monthly_installment_amount': _('مبلغ هر قسط'),
            'is_settled': _('تسویه شده؟'),
        }
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_installment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_installment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'monthly_installment_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_settled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        # Get organization instance from kwargs if passed from the view
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)

        # Filter employee choices based on the organization
        # If organization is provided (e.g., from URL or initial data)
        if organization:
            # Filter employees who are associated with this organization through EmployeeOrganization
            self.fields['employee'].queryset = Employee.objects.filter(employee_organizations__organization=organization).distinct()
            # Optional: If employee is fixed (e.g., in initial data from URL), disable the field
            if 'employee' in self.initial:
                 self.fields['employee'].disabled = True
                 self.fields['employee'].empty_label = None # Remove "---------" option

        # Optional: If organization is fixed (e.g., in initial data from URL), disable the field
        if 'organization' in self.initial:
             self.fields['organization'].disabled = True
             self.fields['organization'].empty_label = None


    # Optional: Add custom validation
    # def clean(self):
    #     cleaned_data = super().clean()
    #     first_date = cleaned_data.get('first_installment_date')
    #     last_date = cleaned_data.get('last_installment_date')
    #     if first_date and last_date and first_date > last_date:
    #         raise forms.ValidationError(_("تاریخ اولین قسط نمی‌تواند بعد از تاریخ آخرین قسط باشد."))
    #     return cleaned_data

