from django.db import models
from django.conf import settings # برای ارجاع به مدل User جنگو
from django.utils.translation import gettext_lazy as _ # برای استفاده از ترجمه در verbose_name
from django.core.exceptions import ValidationError # برای اعتبارسنجی در متد clean()
from django.db.models import Q # برای استفاده در clean()

# مدل اصلی سازمان
class Organization(models.Model):
    """
    مدلی برای ذخیره اطلاعات سازمان‌ها.
    هر سازمان دارای نام، کد و اطلاعات تماس است.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_("نام سازمان"))
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=_("کد سازمان"))
    address = models.TextField(blank=True, null=True, verbose_name=_("آدرس"))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("شماره تماس"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("ایمیل"))
    website = models.URLField(blank=True, null=True, verbose_name=_("وب‌سایت"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("سازمان")
        verbose_name_plural = _("سازمان‌ها")
        ordering = ['name'] # مرتب سازی پیش فرض بر اساس نام

    def __str__(self):
        return self.name

# مدل واسط برای ارتباط کارمند با سازمان (اگر یک کارمند می‌تواند در چند سازمان باشد)
# این مدل همچنان به مدل Employee در اپ employees نیاز دارد.
# بنابراین باید Employee را از employees.models وارد کند.
class EmployeeOrganization(models.Model):
    """
    مدل واسط برای تعریف عضویت یک کارمند در یک سازمان خاص.
    شامل تاریخ شروع و پایان عضویت.
    """
    # ارجاع به مدل Employee در اپ employees
    employee = models.ForeignKey(
        'employees.Employee', # ارجاع با استفاده از 'app_label.ModelName'
        on_delete=models.CASCADE,
        related_name='employee_organizations',
        verbose_name=_("کارمند")
    )
    # ارجاع به مدل Organization در همین اپ (organizations)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employee_organizations',
        verbose_name=_("سازمان")
    )
    start_date = models.DateField(verbose_name=_("تاریخ شروع عضویت"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("تاریخ پایان عضویت"))
    is_active = models.BooleanField(default=True, verbose_name=_("عضویت فعال"))

    class Meta:
        verbose_name = _("عضویت کارمند در سازمان")
        verbose_name_plural = _("عضویت‌های کارمندان در سازمان‌ها")
        # اضافه کردن محدودیت برای جلوگیری از عضویت تکراری یک کارمند در یک سازمان خاص در یک بازه زمانی
        constraints = [
             models.UniqueConstraint(fields=['employee', 'organization', 'start_date'], name='unique_employee_organization_start'),
             # بررسی عدم همپوشانی بازه‌های زمانی در متد clean() انجام می‌شود.
        ]
        ordering = ['organization', 'employee', 'start_date'] # مرتب سازی پیش فرض

    # def clean(self):
    #     """
    #     اعتبارسنجی برای اطمینان از عدم همپوشانی بازه‌های عضویت یک کارمند در یک سازمان.
    #     """
    #     # اعتبارسنجی اولیه: تاریخ شروع باید قبل یا همزمان با تاریخ پایان باشد (اگر تاریخ پایان وجود دارد)
    #     if self.start_date and self.end_date and self.start_date > self.end_date:
    #         raise ValidationError(_("تاریخ شروع عضویت نمی‌تواند بعد از تاریخ پایان باشد."))

    #     # بررسی عدم همپوشانی با عضویت‌های موجود برای همان کارمند و سازمان
    #     if self.employee and self.organization and self.start_date:
    #          # فیلتر کردن عضویت‌های موجود برای همان کارمند و سازمان
    #          # که بازه زمانی آن‌ها با بازه زمانی شیء فعلی همپوشانی دارد
    #          # دو بازه [A, B] و [C, D] همپوشانی دارند اگر A <= D و C <= B
    #          # در اینجا، بازه موجود [eo.start_date, eo.end_date] و بازه جدید [self.start_date, self.end_date] است.

    #          overlapping_memberships = EmployeeOrganization.objects.filter(
    #              employee=self.employee,
    #              organization=self.organization,
    #              # شرط همپوشانی:
    #              # (پایان موجود >= شروع جدید یا پایان موجود نامشخص)
    #              # و (شروع موجود <= پایان جدید یا پایان جدید نامشخص)
    #              Q(end_date__gte=self.start_date) | Q(end_date__isnull=True), # پایان موجود >= شروع جدید یا پایان موجود نامشخص
    #              Q(start_date__lte=self.end_date) | Q(end_date__isnull=True) # شروع موجود <= پایان جدید یا پایان جدید نامشخص (استفاده از end_date__isnull=True برای پایان جدید نامشخص)
    #          ).exclude(pk=self.pk) # exclude کردن شیء فعلی در زمان ویرایش (تا با خودش همپوشانی محسوب نشود)

    #          if overlapping_memberships.exists():
    #               # اگر هر گونه همپوشانی یافت شد، خطای اعتبارسنجی را ایجاد کن
    #               raise ValidationError(_("این بازه عضویت با یک بازه عضویت موجود برای این کارمند در این سازمان همپوشانی دارد."))





    def clean(self):
        """
        اعتبارسنجی برای اطمینان از عدم همپوشانی بازه‌های عضویت یک کارمند در یک سازمان.
        """
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("تاریخ شروع عضویت نمی‌تواند بعد از تاریخ پایان باشد."))

        if self.employee and self.organization and self.start_date:
            overlapping_memberships = EmployeeOrganization.objects.filter(
                employee=self.employee,
                organization=self.organization
            ).filter(
                # ترکیب صحیح شروط همپوشانی:
                (Q(end_date__gte=self.start_date) | Q(end_date__isnull=True)) &
                (Q(start_date__lte=self.end_date) | Q(end_date__isnull=True))
            ).exclude(pk=self.pk)

            if overlapping_memberships.exists():
                raise ValidationError(_("این بازه عضویت با یک بازه عضویت موجود برای این کارمند در این سازمان همپوشانی دارد."))

    def __str__(self):
        return f"{self.employee} در {self.organization} ({self.start_date} - {self.end_date if self.end_date else 'تاکنون'})"

