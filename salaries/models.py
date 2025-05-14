from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q

# Import models from other apps using the 'app_label.ModelName' format
from organizations.models import Organization
from employees.models import Employee
from settings_app.models import FinancialPeriod # Assuming FinancialPeriod is the relevant model for periods


class SalaryItemType(models.Model):
    """
    مدلی برای تعریف انواع آیتم‌های حقوقی (مانند حقوق پایه، اضافه کاری، کسر مالیات).
    این آیتم‌ها به سازمان و دوره مالی مرتبط هستند.
    """

    ITEM_TYPE_CHOICES = [
        ('monthly', _('ماهیانه')),
        ('daily', _('روزانه')),
        ('other', _('سایر')), # برای انعطاف بیشتر
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='salary_item_types',
        verbose_name=_("سازمان")
    )
    financial_period = models.ForeignKey(
        FinancialPeriod,
        on_delete=models.CASCADE,
        related_name='salary_item_types',
        verbose_name=_("دوره مالی")
    )
    name = models.CharField(max_length=100, verbose_name=_("نام آیتم حقوقی"))
    item_type = models.CharField(
        max_length=10,
        choices=ITEM_TYPE_CHOICES,
        default='monthly',
        verbose_name=_("نوع محاسبه")
    )
    is_base_salary = models.BooleanField(
        default=False,
        verbose_name=_("جز حقوق پایه است؟"),
        help_text=_("آیا این آیتم بخشی از حقوق پایه کارمند محسوب می‌شود؟")
    )
    is_deduction = models.BooleanField(
        default=False,
        verbose_name=_("کسر از حقوق است؟"),
        help_text=_("آیا این آیتم باعث کسر از حقوق کارمند می‌شود؟ (مانند مالیات یا بیمه)")
    )
    # Note: The default amount could be added here if needed,
    # but the requirement implies the amount is specific to the employee and period.

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("نوع آیتم حقوقی")
        verbose_name_plural = _("انواع آیتم‌های حقوقی")
        # Ensure the name is unique within a financial period for a given organization
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'financial_period', 'name'],
                name='unique_salary_item_type_per_org_period'
            )
        ]
        ordering = ['organization', 'financial_period', 'name']

    def __str__(self):
        return f"{self.name} ({self.organization.name}, {self.financial_period.name})"


class EmployeeSalaryItem(models.Model):
    """
    مدلی برای ثبت مبلغ یک آیتم حقوقی خاص برای یک کارمند در یک دوره مالی مشخص.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_items',
        verbose_name=_("کارمند")
    )
    financial_period = models.ForeignKey(
        FinancialPeriod,
        on_delete=models.CASCADE,
        related_name='employee_salary_items',
        verbose_name=_("دوره مالی")
    )
    salary_item_type = models.ForeignKey(
        SalaryItemType,
        on_delete=models.CASCADE,
        related_name='employee_salary_items',
        verbose_name=_("نوع آیتم حقوقی")
    )
    amount = models.DecimalField(
        max_digits=15, # Adjust max_digits and decimal_places as needed for currency
        decimal_places=2,
        verbose_name=_("مبلغ")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("آیتم حقوقی کارمند")
        verbose_name_plural = _("آیتم‌های حقوقی کارکنان")
        # Ensure a specific salary item type is recorded only once
        # for a given employee in a given financial period
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'financial_period', 'salary_item_type'],
                name='unique_employee_salary_item_per_period'
            )
        ]
        ordering = ['financial_period', 'employee', 'salary_item_type__name']

    def __str__(self):
        return f"{self.employee} - {self.salary_item_type.name} ({self.financial_period.name}): {self.amount}"

# Versioning (Requirement 6) - Mentioned as an enhancement
# Implementing versioning requires additional logic or libraries like django-reversion.
# This would involve registering the models (SalaryItemType, EmployeeSalaryItem)
# with the versioning system.
