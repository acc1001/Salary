from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import Permission # Import Permission model

# Import CustomUser model from the current app
from .models import CustomUser, OrganizationRole, UserOrganizationRole

# Import Organization model from the organizations app
from organizations.models import Organization


class CustomAuthenticationForm(AuthenticationForm):
    """
    فرم ورود سفارشی با استایل بوت استرپ.
    """
    username = forms.CharField(
        label=_("نام کاربری"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label=_("رمز عبور"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class CustomUserCreationForm(UserCreationForm):
    """
    فرم ثبت نام کاربر جدید با مدل کاربری سفارشی و فیلدهای اضافی.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',) # اضافه کردن فیلدهای اضافی
        labels = { # برچسب‌های فارسی
            'username': _('نام کاربری'),
            'first_name': _('نام'),
            'last_name': _('نام خانوادگی'),
            'email': _('ایمیل'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CustomUserChangeForm(UserChangeForm):
    """
    فرم ویرایش اطلاعات کاربر با مدل کاربری سفارشی.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        labels = { # برچسب‌های فارسی
            'username': _('نام کاربری'),
            'first_name': _('نام'),
            'last_name': _('نام خانوادگی'),
            'email': _('ایمیل'),
            'is_active': _('فعال'),
            'is_staff': _('کارمند'),
            'is_superuser': _('ابرکاربر'),
            'groups': _('گروه‌ها'),
            'user_permissions': _('مجوزهای کاربر'),
        }
        widgets = { # ویجت‌ها با کلاس بوت استرپ
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class OrganizationRoleForm(forms.ModelForm):
    """
    فرم مدل برای ایجاد و ویرایش نقش‌های سازمانی.
    """
    class Meta:
        model = OrganizationRole
        fields = ['organization', 'name', 'description', 'permissions']
        labels = {
            'organization': _('سازمان'),
            'name': _('نام نقش'),
            'description': _('توضیحات'),
            'permissions': _('مجوزها'),
        }
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permissions': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    # Optional: Filter organization choices based on user permissions
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Example: Only show organizations the user has permission to manage roles for
    #     # if not self.request.user.is_superuser:
    #     #     managed_orgs = self.request.user.get_managed_organizations() # Assuming such a method exists
    #     #     self.fields['organization'].queryset = Organization.objects.filter(pk__in=[org.pk for org in managed_orgs])


class UserOrganizationRoleForm(forms.ModelForm):
    """
    فرم مدل برای انتساب نقش سازمانی به کاربر.
    """
    class Meta:
        model = UserOrganizationRole
        fields = ['user', 'organization', 'role']
        labels = {
            'user': _('کاربر'),
            'organization': _('سازمان'),
            'role': _('نقش'),
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Get organization instance from kwargs if passed from the view
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)

        # Filter role choices based on the organization
        if organization:
            self.fields['role'].queryset = OrganizationRole.objects.filter(organization=organization)
            # Optional: If organization is fixed, disable the field
            if 'organization' in self.initial:
                 self.fields['organization'].disabled = True
                 self.fields['organization'].empty_label = None # Remove "---------" option

        # Optional: Filter user choices if needed (e.g., users not already having a role in this org)
        # if organization:
        #     users_with_role = UserOrganizationRole.objects.filter(organization=organization).values_list('user', flat=True)
        #     self.fields['user'].queryset = CustomUser.objects.exclude(pk__in=users_with_role)

