from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal # Use Decimal for currency fields

# Import necessary models from other apps
from employees.models import Employee # Loans are given to employees
from organizations.models import Organization # Loans are linked to an organization


class EmployeeLoan(models.Model):
    """
    مدلی برای ذخیره اطلاعات وام‌های اعطا شده به کارکنان.
    شامل جزئیات وام، تاریخ‌های اقساط و وضعیت تسویه.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='employee_loans',
        verbose_name=_("کارمند")
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employee_loans',
        verbose_name=_("سازمان")
    )
    loan_amount = models.DecimalField(
        max_digits=15, # Adjust as needed for currency
        decimal_places=2,
        verbose_name=_("مبلغ وام دریافتی")
    )
    first_installment_date = models.DateField(verbose_name=_("تاریخ اولین قسط"))
    last_installment_date = models.DateField(verbose_name=_("تاریخ آخرین قسط"))
    monthly_installment_amount = models.DecimalField(
        max_digits=15, # Adjust as needed for currency
        decimal_places=2,
        verbose_name=_("مبلغ هر قسط")
    )
    is_settled = models.BooleanField(
        default=False,
        verbose_name=_("تسویه شده؟"),
        help_text=_("آیا این وام به طور کامل تسویه شده است؟")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ثبت"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("وام کارمند")
        verbose_name_plural = _("وام‌های کارکنان")
        # Optional: Add a constraint if an employee can only have one active loan per organization at a time,
        # but based on requirements, a simple list is expected, so no unique constraint on employee/org needed here.
        ordering = ['employee', '-first_installment_date'] # Order by employee, then newest first

    def __str__(self):
        return f"وام به {self.employee} در {self.organization.name} (مبلغ: {self.loan_amount}, تسویه: {self.is_settled})"

    # Optional: Add properties for calculated fields if needed, e.g., total paid, remaining balance
    # This would require a separate model for payments if you need to track individual payments.
    # Based on current requirements, only the total loan and installment amount are needed.

