from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Department, JobTitle, EmploymentHistory, MonthlyWorkRecord

# Import models from other apps if needed for form fields (e.g., ForeignKey choices)
from organizations.models import Organization
from employees.models import Employee
from settings_app.models import FinancialPeriod
from django.db.models import Q # Import Q for complex lookups


class DepartmentForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات دپارتمان.
    """
    class Meta:
        model = Department
        fields = ['organization', 'name', 'description', 'is_active']
        labels = {
            'organization': _('سازمان'),
            'name': _('نام دپارتمان'),
            'description': _('توضیحات'),
            'is_active': _('فعال'),
        }
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # Optional: Filter organization choices if needed (e.g., based on current user)
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Example: Filter organizations based on user permissions
    #     # self.fields['organization'].queryset = Organization.objects.filter(...)


class JobTitleForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش عناوین شغلی.
    """
    class Meta:
        model = JobTitle
        fields = ['organization', 'title', 'description', 'is_active']
        labels = {
            'organization': _('سازمان'),
            'title': _('عنوان شغلی'),
            'description': _('توضیحات'),
            'is_active': _('فعال'),
        }
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # Optional: Filter organization choices if needed
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.fields['organization'].queryset = Organization.objects.filter(...)


class EmploymentHistoryForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش سابقه شغلی کارمند.
    فیلتر کردن دپارتمان‌ها و عناوین شغلی بر اساس سازمان انتخاب شده.
    """
    class Meta:
        model = EmploymentHistory
        fields = ['employee', 'organization', 'department', 'job_title', 'start_date', 'end_date', 'is_current', 'responsibilities', 'notes']
        labels = {
            'employee': _('کارمند'),
            'organization': _('سازمان'),
            'department': _('دپارتمان'),
            'job_title': _('عنوان شغلی'),
            'start_date': _('تاریخ شروع'),
            'end_date': _('تاریخ پایان'),
            'is_current': _('فعلی؟'),
            'responsibilities': _('مسئولیت‌ها'),
            'notes': _('ملاحظات'),
        }
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Get organization instance from kwargs if passed from the view
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)

        # Filter department and job_title choices based on the organization
        # If organization is provided (e.g., from URL or initial data)
        if organization:
            self.fields['department'].queryset = Department.objects.filter(organization=organization)
            # Filter job titles by the specific organization or those with no organization (general)
            self.fields['job_title'].queryset = JobTitle.objects.filter(Q(organization=organization) | Q(organization__isnull=True))
        else:
            # If no organization is provided, initially show empty choices or a default message
            # This might require JavaScript to dynamically load options based on organization selection
            # For now, show empty queryset if no organization is specified
            self.fields['department'].queryset = Department.objects.none()
            self.fields['job_title'].queryset = JobTitle.objects.none() # Or show all if general titles are always an option

        # Optional: Filter employee choices if needed (e.g., employees in the selected organization)
        # if organization:
        #      self.fields['employee'].queryset = Employee.objects.filter(employee_organizations__organization=organization).distinct()


class MonthlyWorkRecordForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش اطلاعات کارکرد ماهیانه.
    فیلتر کردن کارمند، سازمان و دوره مالی بر اساس نیاز.
    """
    class Meta:
        model = MonthlyWorkRecord
        fields = [
            'employee',
            'organization',
            'financial_period',
            'monthly_working_hours',
            'working_days_in_month',
            'standard_hours_in_month',
            'overtime_hours',
            'deficit_hours',
            'used_leave_days',
            'used_leave_hours',
            'friday_holiday_workdays',
            'mission_days',
        ]
        labels = {
            'employee': _('کارمند'),
            'organization': _('سازمان'),
            'financial_period': _('دوره مالی'),
            'monthly_working_hours': _('ساعات کارکرد در ماه'),
            'working_days_in_month': _('روزهای کاری در ماه'),
            'standard_hours_in_month': _('ساعت استاندارد در ماه'),
            'overtime_hours': _('ساعات اضافه کاری'),
            'deficit_hours': _('ساعات کسر کاری'),
            'used_leave_days': _('روزهای مرخصی استفاده شده'),
            'used_leave_hours': _('ساعات مرخصی استفاده شده'),
            'friday_holiday_workdays': _('روزهای جمعه کاری یا تعطیل کاری'),
            'mission_days': _('روزهای ماموریت'),
        }
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'financial_period': forms.Select(attrs={'class': 'form-control'}),
            'monthly_working_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'working_days_in_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'standard_hours_in_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'deficit_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'used_leave_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'used_leave_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'friday_holiday_workdays': forms.NumberInput(attrs={'class': 'form-control'}),
            'mission_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Get filtering objects from kwargs if passed from the view
        employee = kwargs.pop('employee', None)
        organization = kwargs.pop('organization', None)
        financial_period = kwargs.pop('financial_period', None)
        super().__init__(*args, **kwargs)

        # Filter choices based on provided objects
        if employee:
            self.fields['employee'].queryset = Employee.objects.filter(pk=employee.pk)
            self.fields['employee'].empty_label = None # Prevent "---------" option if employee is fixed
            self.fields['employee'].disabled = True # Disable field if fixed

        if organization:
            self.fields['organization'].queryset = Organization.objects.filter(pk=organization.pk)
            self.fields['organization'].empty_label = None
            self.fields['organization'].disabled = True

            # Filter financial periods by the selected organization
            self.fields['financial_period'].queryset = FinancialPeriod.objects.filter(organization=organization)
        elif financial_period: # If only financial_period is provided, filter by its organization
             self.fields['organization'].queryset = Organization.objects.filter(pk=financial_period.organization.pk)
             self.fields['organization'].empty_label = None
             self.fields['organization'].disabled = True
             self.fields['financial_period'].queryset = FinancialPeriod.objects.filter(pk=financial_period.pk)
             self.fields['financial_period'].empty_label = None
             self.fields['financial_period'].disabled = True
        else:
            # If no organization or financial period is provided, show all organizations and periods
            # Or implement JavaScript filtering based on organization selection
            pass # Keep default queryset or set to none() initially if dynamic loading is used

        # Optional: Filter employees based on organization if organization is selected/available
        # if organization:
        #      self.fields['employee'].queryset = Employee.objects.filter(employee_organizations__organization=organization).distinct()

