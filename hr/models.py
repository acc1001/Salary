from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q

# Import necessary models from other apps
from organizations.models import Organization # To link departments, job titles, and work records to an organization
from employees.models import Employee # To link employment history and work records to an employee
from settings_app.models import FinancialPeriod # To link work records to a financial period


class Department(models.Model):
    """
    مدلی برای ذخیره اطلاعات دپارتمان‌های مختلف در سازمان‌ها.
    هر دپارتمان به یک سازمان مرتبط است.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_("سازمان")
    )
    name = models.CharField(max_length=255, verbose_name=_("نام دپارتمان"))
    description = models.TextField(blank=True, null=True, verbose_name=_("توضیحات"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("دپارتمان")
        verbose_name_plural = _("دپارتمان‌ها")
        # Ensure department name is unique within an organization
        constraints = [
            models.UniqueConstraint(fields=['organization', 'name'], name='unique_department_name_per_org')
        ]
        ordering = ['organization', 'name']

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class JobTitle(models.Model):
    """
    مدلی برای ذخیره اطلاعات عناوین شغلی.
    عناوین شغلی می‌توانند به یک سازمان خاص مرتبط باشند یا عمومی باشند.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='job_titles',
        verbose_name=_("سازمان"),
        blank=True, # Job titles can be organization-specific or general
        null=True,
        help_text=_("سازمانی که این عنوان شغلی به آن مرتبط است (اختیاری).")
    )
    title = models.CharField(max_length=255, verbose_name=_("عنوان شغلی"))
    description = models.TextField(blank=True, null=True, verbose_name=_("توضیحات"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("عنوان شغلی")
        verbose_name_plural = _("عناوین شغلی")
        # Ensure job title is unique within an organization OR globally unique if organization is null
        # This requires a custom clean method or more complex constraint setup if strictly needed.
        # Adding a simple unique constraint on organization and title.
        constraints = [
            models.UniqueConstraint(fields=['organization', 'title'], name='unique_job_title_per_org'),
            # Consider adding a check constraint to ensure title is unique if organization is null
        ]
        ordering = ['organization__name', 'title'] # Order by organization first, then title

    def __str__(self):
        if self.organization:
            return f"{self.title} ({self.organization.name})"
        return self.title


class EmploymentHistory(models.Model):
    """
    مدلی برای ثبت سابقه شغلی یک کارمند.
    شامل اطلاعات موقعیت شغلی، دپارتمان، سازمان و بازه زمانی اشتغال.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='employment_history',
        verbose_name=_("کارمند")
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employment_history',
        verbose_name=_("سازمان")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL, # If a department is deleted, don't delete the history
        related_name='employment_history',
        verbose_name=_("دپارتمان"),
        blank=True,
        null=True
    )
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.SET_NULL, # If a job title is deleted, don't delete the history
        related_name='employment_history',
        verbose_name=_("عنوان شغلی"),
        blank=True,
        null=True
    )
    start_date = models.DateField(verbose_name=_("تاریخ شروع"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("تاریخ پایان"))
    is_current = models.BooleanField(
        default=True,
        verbose_name=_("فعلی؟"),
        help_text=_("آیا این موقعیت شغلی فعلی کارمند است؟")
    )
    responsibilities = models.TextField(blank=True, null=True, verbose_name=_("مسئولیت‌ها"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("سابقه شغلی")
        verbose_name_plural = _("سوابق شغلی")
        # Order by start date descending, then end date descending (current positions first)
        ordering = ['employee', '-start_date', '-end_date']

        # Constraint to prevent overlapping employment history for the same employee in the same organization
        # This is complex and better handled in the clean method or form validation.
        # Adding a unique constraint on employee, organization, and start_date for basic uniqueness.
        constraints = [
            models.UniqueConstraint(fields=['employee', 'organization', 'start_date'], name='unique_employment_start_per_employee_org'),
        ]

    def clean(self):
        """
        Custom validation to prevent overlapping employment history dates for the same employee in the same organization.
        Also ensures start date is not after end date.
        """
        # Ensure start date is not after end date
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد."))

        # Check for overlapping history for the same employee and organization
        if self.employee and self.organization and self.start_date:
             # Find existing history entries for the same employee and organization
             # that overlap with the current entry's date range [self.start_date, self.end_date]
             # Two ranges [A, B] and [C, D] overlap if A <= D and C <= B
            overlapping_history = EmploymentHistory.objects.filter(
                employee=self.employee,
                organization=self.organization
            ).filter(
                # Overlap condition:
                # (existing_end_date >= new_start_date OR existing_end_date is null)
                # AND (existing_start_date <= new_end_date OR new_end_date is null)
                (Q(end_date__gte=self.start_date) | Q(end_date__isnull=True)) &
                (Q(start_date__lte=self.end_date) | Q(end_date__isnull=True))
            ).exclude(pk=self.pk) # Exclude the current object itself when updating

            if overlapping_history.exists():
                raise ValidationError(_("این بازه سابقه شغلی با یک سابقه شغلی موجود برای این کارمند در این سازمان همپوشانی دارد."))

        # Ensure only one history entry is marked as 'is_current' for a given employee
        if self.is_current and self.employee:
            current_positions = EmploymentHistory.objects.filter(
                employee=self.employee,
                is_current=True
            ).exclude(pk=self.pk) # Exclude the current object

            if current_positions.exists():
                 # You might want to automatically set is_current=False for the existing one
                 # or raise a validation error. Raising error for now.
                 raise ValidationError(_("فقط یک سابقه شغلی برای هر کارمند می‌تواند به عنوان موقعیت فعلی علامت‌گذاری شود."))


    def save(self, *args, **kwargs):
        # Optional: Automatically set is_current=False for other entries
        # if this one is marked as current
        if self.is_current and self.employee:
            EmploymentHistory.objects.filter(
                employee=self.employee
            ).exclude(pk=self.pk).update(is_current=False)

        super().save(*args, **kwargs)


    def __str__(self):
        period = f"{self.start_date} - {self.end_date if self.end_date else 'تاکنون'}"
        return f"{self.employee} در {self.job_title} ({self.organization.name}, {period})"


class MonthlyWorkRecord(models.Model):
    """
    مدلی برای ذخیره اطلاعات کارکرد ماهیانه یک کارمند در یک سازمان و دوره مالی مشخص.
    این مدل شامل ساعات کارکرد، مرخصی، ماموریت و ... در یک ماه است.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='monthly_work_records',
        verbose_name=_("کارمند")
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='monthly_work_records',
        verbose_name=_("سازمان")
    )
    financial_period = models.ForeignKey(
        FinancialPeriod,
        on_delete=models.CASCADE,
        related_name='monthly_work_records',
        verbose_name=_("دوره مالی")
    )

    # Fields based on your requirements
    monthly_working_hours = models.DecimalField(
        max_digits=10, # Adjust as needed
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات کارکرد در ماه")
    )
    working_days_in_month = models.DecimalField( # Using DecimalField for potential half-days
        max_digits=5, # Adjust as needed
        decimal_places=1,
        default=0,
        verbose_name=_("روزهای کاری در ماه")
    )
    standard_hours_in_month = models.DecimalField(
        max_digits=10, # Adjust as needed
        decimal_places=2,
        default=0,
        verbose_name=_("ساعت استاندارد در ماه")
    )
    overtime_hours = models.DecimalField(
        max_digits=10, # Adjust as needed
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات اضافه کاری")
    )
    deficit_hours = models.DecimalField(
        max_digits=10, # Adjust as needed
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات کسر کاری")
    )
    used_leave_days = models.DecimalField( # Using DecimalField for potential half-days
        max_digits=5, # Adjust as needed
        decimal_places=1,
        default=0,
        verbose_name=_("روزهای مرخصی استفاده شده")
    )
    used_leave_hours = models.DecimalField(
        max_digits=10, # Adjust as needed
        decimal_places=2,
        default=0,
        verbose_name=_("ساعات مرخصی استفاده شده")
    )
    friday_holiday_workdays = models.DecimalField( # Using DecimalField for potential partial days
        max_digits=5, # Adjust as needed
        decimal_places=1,
        default=0,
        verbose_name=_("روزهای جمعه کاری یا تعطیل کاری")
    )
    mission_days = models.DecimalField( # Using DecimalField for potential partial days
        max_digits=5, # Adjust as needed
        decimal_places=1,
        default=0,
        verbose_name=_("روزهای ماموریت")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("کارکرد ماهیانه")
        verbose_name_plural = _("کارکرد ماهیانه کارکنان")
        # Ensure a specific employee has only one work record per organization and financial period
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'organization', 'financial_period'],
                name='unique_monthly_work_record_per_employee_org_period'
            )
        ]
        ordering = ['financial_period', 'employee']

    def __str__(self):
        return f"کارکرد {self.employee} در {self.organization.name} ({self.financial_period.name})"

# Note on Versioning (Requirement 6 from previous salary app):
# Implementing versioning for these models (Department, JobTitle, EmploymentHistory, MonthlyWorkRecord)
# would require additional logic or libraries like django-reversion, as mentioned before.
