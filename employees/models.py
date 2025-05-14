from django.db import models
from django.conf import settings # برای ارجاع به مدل User جنگو
from django.utils.translation import gettext_lazy as _ # برای استفاده از ترجمه در verbose_name
import os # برای کار با مسیرهای فایل

# تابع برای تعیین مسیر آپلود تصویر پرسنلی
def employee_image_upload_path(instance, filename):
    """
    تعیین مسیر آپلود برای تصویر پرسنلی کارمندان.
    فایل‌ها در مسیر 'employees/photos/<employee_id>/<filename>' ذخیره می‌شوند.
    """
    # نام فایل را به صورت ایمن‌تر و بدون کاراکترهای خاص در نظر بگیرید
    # در اینجا فقط از نام اصلی فایل استفاده می‌کنیم، می‌توانید آن را تغییر دهید
    filename_base, filename_ext = os.path.splitext(filename)
    # می‌توانید از کد ملی یا کد پرسنلی به جای pk استفاده کنید اگر منحصر به فرد هستند
    # return f'employees/photos/{instance.national_code}/{filename}'
    return f'employees/photos/{instance.pk}/{filename}'


class Employee(models.Model):
    """
    مدلی برای ذخیره اطلاعات اصلی کارمندان.
    هر کارمند به یک حساب کاربری جنگو مرتبط است.
    """
    user_account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name=_("حساب کاربری")
    )
    first_name = models.CharField(max_length=100, verbose_name=_("نام"))
    last_name = models.CharField(max_length=100, verbose_name=_("نام خانوادگی"))
    national_code = models.CharField(max_length=10, unique=True, verbose_name=_("کد ملی"))
    personnel_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=_("کد پرسنلی"))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("تاریخ تولد"))
    hire_date = models.DateField(verbose_name=_("تاریخ استخدام"))
    fire_date = models.DateField(blank=True, null=True, verbose_name=_("تاریخ پایان همکاری")) # تاریخ اخراج یا اتمام قرارداد
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    # اضافه کردن فیلد تصویر پرسنلی با استفاده از تابع آپلود
    photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=employee_image_upload_path, # <--- استفاده از تابع تعریف شده
        verbose_name=_("تصویر پرسنلی")
    )

    # ارتباط با سازمان‌ها از طریق مدل واسط EmployeeOrganization در اپ organizations
    # organizations = models.ManyToManyField(
    #     'organizations.Organization', # ارجاع به مدل Organization در اپ organizations
    #     through='organizations.EmployeeOrganization', # استفاده از مدل واسط در اپ organizations
    #     related_name='employees',
    #     verbose_name=_("سازمان‌ها")
    # )
    # نکته: فیلد ManyToManyField در اینجا اختیاری است. اگر فقط از مدل واسط EmployeeOrganization
    # برای مدیریت ارتباط استفاده می‌کنید، نیازی به تعریف این فیلد در مدل Employee نیست.
    # ارتباط از طریق related_name='employee_organizations' در مدل EmployeeOrganization
    # امکان دسترسی به عضویت‌های کارمند را فراهم می‌کند: employee.employee_organizations.all()


    class Meta:
        verbose_name = _("کارمند")
        verbose_name_plural = _("کارکنان")
        ordering = ['last_name', 'first_name'] # مرتب سازی پیش فرض

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # می‌توانید متدهای کمکی برای دسترسی به سازمان‌های فعال یا فعلی اضافه کنید
    # def get_current_organizations(self):
    #     from organizations.models import EmployeeOrganization # import داخلی برای جلوگیری از Circular Import
    #     return Organization.objects.filter(employeeorganization__employee=self, employeeorganization__is_active=True)


class BankAccount(models.Model):
    """
    مدلی برای ذخیره اطلاعات حساب بانکی کارمندان.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        verbose_name=_("کارمند")
    )
    bank_name = models.CharField(max_length=100, verbose_name=_("نام بانک"))
    account_number = models.CharField(max_length=50, verbose_name=_("شماره حساب"))
    card_number = models.CharField(max_length=19, blank=True, null=True, verbose_name=_("شماره کارت")) # معمولا ۱۶ رقم + ۳ رقم CVV2
    sheba_number = models.CharField(max_length=26, unique=True, blank=True, null=True, verbose_name=_("شماره شبا")) # IR + 24 رقم
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("حساب بانکی")
        verbose_name_plural = _("حساب‌های بانکی")
        # اضافه کردن محدودیت برای جلوگیری از تکرار شماره حساب برای یک کارمند در یک بانک خاص
        constraints = [
             models.UniqueConstraint(fields=['employee', 'bank_name', 'account_number'], name='unique_bank_account_per_employee_bank')
        ]

    def __str__(self):
        return f"{self.employee} - {self.bank_name} ({self.account_number})"

