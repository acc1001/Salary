from django.db import models
# اطمینان از import مدل Organization از اپ organizations
from organizations.models import Organization # <--- این خط تغییر می‌کند
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ # برای استفاده از ترجمه در verbose_name
from django.db.models import Q, F # برای استفاده در CheckConstraint و clean


class FiscalYear(models.Model):
    """
    مدلی برای ذخیره اطلاعات سال‌های مالی مرتبط با هر سازمان.
    هر سال مالی دارای یک عنوان، تاریخ شروع و پایان است.
    """
    organization = models.ForeignKey(
        Organization, # <--- این ارجاع اکنون به مدل در اپ organizations است
        on_delete=models.CASCADE,
        related_name='fiscal_years',
        verbose_name=_("سازمان") # verbose_name فارسی
    )
    title = models.CharField(max_length=100, verbose_name=_("عنوان سال مالی"))
    start_date = models.DateField(verbose_name=_("تاریخ شروع"))
    end_date = models.DateField(verbose_name=_("تاریخ پایان"))

    class Meta:
        verbose_name = _("سال مالی") # verbose_name فارسی
        verbose_name_plural = _("سال‌های مالی") # verbose_name_plural فارسی
        # اضافه کردن محدودیت برای اطمینان از منحصر به فرد بودن عنوان سال مالی در یک سازمان
        constraints = [
            models.UniqueConstraint(fields=['organization', 'title'], name='unique_fiscal_year_title_per_org'),
            # اطمینان از اینکه تاریخ شروع قبل از تاریخ پایان است
            models.CheckConstraint(check=Q(start_date__lt=F('end_date')), name='fiscal_year_start_before_end')
        ]
        # مرتب سازی پیش فرض بر اساس تاریخ شروع
        ordering = ['start_date']


    def clean(self):
        """
        اعتبارسنجی برای اطمینان از عدم همپوشانی با سال‌های مالی موجود برای همان سازمان.
        """
        if self.organization and self.start_date and self.end_date:
            overlapping_years = FiscalYear.objects.filter(
                organization=self.organization,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            ).exclude(pk=self.pk) # exclude کردن شیء فعلی در زمان ویرایش

            if overlapping_years.exists():
                 raise ValidationError(_("این سال مالی با یک سال مالی موجود برای این سازمان همپوشانی دارد."))


    def __str__(self):
        return f"{self.organization} - {self.title}"

class InsuranceCeiling(models.Model):
    """
    مدلی برای ذخیره سقف مبلغ بیمه برای هر سال مالی مشخص.
    """
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.CASCADE,
        related_name='insurance_ceilings',
        verbose_name=_("سال مالی")
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_("مبلغ سقف بیمه")
    )

    class Meta:
        verbose_name = _("سقف بیمه") # verbose_name فارسی
        verbose_name_plural = _("سقف‌های بیمه") # verbose_name_plural فارسی
        # اضافه کردن محدودیت برای اطمینان از اینکه فقط یک سقف بیمه برای هر سال مالی وجود دارد
        constraints = [
            models.UniqueConstraint(fields=['fiscal_year'], name='unique_insurance_ceiling_per_year')
        ]

    def __str__(self):
        return f"{self.fiscal_year} - سقف بیمه"

class TaxLevel(models.Model):
    """
    مدلی برای تعریف سطوح و درصدهای مالیاتی برای بازه‌های مختلف درآمد در هر سال مالی.
    """
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.CASCADE,
        related_name='tax_levels',
        verbose_name=_("سال مالی")
    )
    level_title = models.CharField(max_length=100, verbose_name=_("عنوان سطح مالیاتی"))
    from_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("از مبلغ"))
    to_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("تا مبلغ"))
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("درصد مالیات"))

    class Meta:
        verbose_name = _("سطح مالیاتی") # verbose_name فارسی
        verbose_name_plural = _("سطوح مالیاتی") # verbose_name_plural فارسی
        # اطمینان از ترتیب صحیح بازه‌ها (from_amount < to_amount)
        constraints = [
             models.CheckConstraint(check=Q(from_amount__lt=F('to_amount')), name='tax_level_from_before_to'),
        ]
        # مرتب سازی بر اساس مبلغ شروع برای نمایش مرتب سطوح
        ordering = ['from_amount']

    def clean(self):
        """
        اعتبارسنجی برای جلوگیری از همپوشانی بازه‌های مالیاتی در یک سال مالی.
        """
        if self.fiscal_year and self.from_amount is not None and self.to_amount is not None:
            overlapping_levels = TaxLevel.objects.filter(
                fiscal_year=self.fiscal_year,
                from_amount__lt=self.to_amount,
                to_amount__gt=self.from_amount
            ).exclude(pk=self.pk) # exclude کردن شیء فعلی در زمان ویرایش

            if overlapping_levels.exists():
                raise ValidationError(_("این بازه مالیاتی با یک بازه موجود در این سال مالی همپوشانی دارد."))

    def __str__(self):
        return f"{self.fiscal_year} - {self.level_title}"


class FinancialPeriod(models.Model):
    """
    مدلی برای تعریف دوره‌های مالی (مانند ماهانه، فصلی) برای محاسبات حقوق.
    این دوره‌ها به یک سال مالی خاص مرتبط هستند.
    """
    # اضافه کردن ForeignKey به FiscalYear
    fiscal_year = models.ForeignKey(
         FiscalYear,
         on_delete=models.CASCADE,
         related_name='financial_periods', # related_name مناسب
         verbose_name=_("سال مالی")
    )
    name = models.CharField(max_length=100, verbose_name=_('نام دوره مالی'))
    start_date = models.DateField(verbose_name=_('تاریخ شروع'))
    end_date = models.DateField(verbose_name=_('تاریخ پایان'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال بودن'))

    class Meta:
        verbose_name = _('دوره مالی') # verbose_name فارسی
        verbose_name_plural = _('دوره‌های مالی') # verbose_name_plural فارسی
        # اضافه کردن محدودیت برای جلوگیری از منحصر به فرد بودن نام دوره مالی در یک سال مالی
        constraints = [
             models.UniqueConstraint(fields=['fiscal_year', 'name'], name='unique_financial_period_name_per_year'),
             # اطمینان از اینکه تاریخ شروع قبل از تاریخ پایان است
             models.CheckConstraint(check=Q(start_date__lt=F('end_date')), name='financial_period_start_before_end')
        ]
        # مرتب سازی بر اساس تاریخ شروع
        ordering = ['start_date']

    def clean(self):
        """
        اعتبارسنجی برای اطمینان از عدم همپوشانی با دوره‌های مالی موجود برای همان سال مالی.
        """
        if self.fiscal_year and self.start_date and self.end_date:
            overlapping_periods = FinancialPeriod.objects.filter(
                fiscal_year=self.fiscal_year,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            ).exclude(pk=self.pk) # exclude کردن شیء فعلی در زمان ویرایش

            if overlapping_periods.exists():
                 raise ValidationError(_("این دوره مالی با یک دوره موجود برای این سال مالی همپوشانی دارد."))


    def __str__(self):
        return f"{self.fiscal_year} - {self.name}"

# نکته: پس از اعمال تغییرات در مدل‌ها، حتماً دستورات makemigrations و migrate را اجرا کنید.
# python manage.py makemigrations settings_app
# python manage.py migrate
