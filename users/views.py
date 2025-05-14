from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages # To add messages manually

# Import forms and models from the current app
from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomUserChangeForm, OrganizationRoleForm, UserOrganizationRoleForm
from .models import CustomUser, OrganizationRole, UserOrganizationRole

# Import Organization model from the organizations app for filtering/context
from organizations.models import Organization


# --- Authentication Views (Existing) ---

class CustomLoginView(LoginView):
    """
    ویو ورود سفارشی.
    """
    authentication_form = CustomAuthenticationForm
    template_name = 'users/login.html'
    # success_url is handled by settings.LOGIN_REDIRECT_URL


class CustomLogoutView(LogoutView):
    """
    ویو خروج سفارشی.
    """
    template_name = 'users/logout.html'
    # next_page is handled by settings.LOGOUT_REDIRECT_URL


class RegisterView(CreateView):
    """
    ویو ثبت نام کاربر جدید.
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login') # Redirect to login after successful registration
    success_message = "حساب کاربری شما با موفقیت ایجاد شد. لطفا وارد شوید."


# --- Views for OrganizationRole (Management of Organization Roles) ---

class OrganizationRoleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست نقش‌های سازمانی.
    فقط برای کاربران مجاز (مثلاً is_staff یا superuser) قابل دسترسی است.
    می‌تواند فیلتر بر اساس سازمان داشته باشد.
    """
    model = OrganizationRole
    template_name = 'users/organizationrole_list.html'
    context_object_name = 'organization_roles'
    # paginate_by = 10 # Optional: Add pagination

    def test_func(self):
        # Only allow staff users or superusers to access this view
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        """
        فیلتر کردن نقش‌های سازمانی بر اساس سازمان مشخص شده در URL.
        """
        organization_pk = self.kwargs.get('organization_pk')
        queryset = OrganizationRole.objects.all()

        if organization_pk:
            queryset = queryset.filter(organization__pk=organization_pk)
            self.organization = get_object_or_404(Organization, pk=organization_pk) # Store organization for context

        # Optional: Filter roles based on user's permissions (e.g., only show roles in organizations they manage)
        # if not self.request.user.is_superuser:
        #     managed_orgs = self.request.user.get_managed_organizations() # Assuming such a method exists
        #     queryset = queryset.filter(organization__in=managed_orgs)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add organization to context if filtered
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        return context


class OrganizationRoleCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد نقش سازمانی جدید.
    فقط برای کاربران مجاز قابل دسترسی است.
    """
    model = OrganizationRole
    form_class = OrganizationRoleForm
    template_name = 'users/organizationrole_form.html'
    success_message = "نقش سازمانی با موفقیت ایجاد شد."

    def test_func(self):
        # Only allow staff users or superusers to access this view
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_initial(self):
        """
        تنظیم مقدار اولیه فیلد سازمان بر اساس URL.
        """
        initial = super().get_initial()
        organization_pk = self.kwargs.get('organization_pk')
        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        return initial

    def get_success_url(self):
        """
        مسیر ریدایرکت پس از ایجاد موفقیت‌آمیز.
        ریدایرکت به لیست نقش‌های سازمانی (ترجیحاً فیلتر شده بر اساس سازمان).
        """
        # Try to redirect to the list filtered by the organization of the created object
        if self.object.organization:
             return reverse_lazy('users:organizationrole_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        # Fallback to general list
        return reverse_lazy('users:organizationrole_list')


class OrganizationRoleUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش نقش سازمانی موجود.
    فقط برای کاربران مجاز قابل دسترسی است.
    """
    model = OrganizationRole
    form_class = OrganizationRoleForm
    template_name = 'users/organizationrole_form.html'
    context_object_name = 'organization_role'
    success_message = "نقش سازمانی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Only allow staff users or superusers to access this view
        # You might also want to check if the user has permission to manage roles in this specific organization
        # return self.request.user.is_staff or self.request.user.is_superuser and self.request.user.can_manage_organization_roles(self.get_object().organization)
        return self.request.user.is_staff or self.request.user.is_superuser


    def get_success_url(self):
        """
        مسیر ریدایرکت پس از ویرایش موفقیت‌آمیز.
        ریدایرکت به لیست نقش‌های سازمانی (ترجیحاً فیلتر شده بر اساس سازمان مرتبط با نقش).
        """
        # Get organization from the object being updated
        organization_pk = self.object.organization.pk
        return reverse_lazy('users:organizationrole_list_by_org', kwargs={'organization_pk': organization_pk})


class OrganizationRoleDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف نقش سازمانی.
    فقط برای کاربران مجاز قابل دسترسی است.
    """
    model = OrganizationRole
    template_name = 'users/organizationrole_confirm_delete.html'
    context_object_name = 'organization_role'
    success_message = "نقش سازمانی با موفقیت حذف شد."

    def test_func(self):
        # Only allow staff users or superusers to access this view
        # You might also want to check if the user has permission to manage roles in this specific organization
        # return self.request.user.is_staff or self.request.user.is_superuser and self.request.user.can_manage_organization_roles(self.get_object().organization)
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_success_url(self):
        """
        مسیر ریدایرکت پس از حذف موفقیت‌آمیز.
        ریدایرکت به لیست نقش‌های سازمانی (ترجیحاً فیلتر شده بر اساس سازمان مرتبط با نقش حذف شده).
        """
        # Get organization from the object being deleted (before it's deleted)
        organization_pk = self.object.organization.pk
        return reverse_lazy('users:organizationrole_list_by_org', kwargs={'organization_pk': organization_pk})

    # Override delete method to add success message manually
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# --- Views for UserOrganizationRole (Assignment of Organization Roles to Users) ---

class UserOrganizationRoleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست انتساب نقش‌های سازمانی به کاربران.
    فقط برای کاربران مجاز قابل دسترسی است.
    می‌تواند فیلتر بر اساس سازمان یا کاربر داشته باشد.
    """
    model = UserOrganizationRole
    template_name = 'users/userorganizationrole_list.html'
    context_object_name = 'user_organization_roles'
    # paginate_by = 10 # Optional: Add pagination

    def test_func(self):
        # Only allow staff users or superusers to access this view
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        """
        فیلتر کردن انتساب‌ها بر اساس سازمان یا کاربر مشخص شده در URL.
        """
        organization_pk = self.kwargs.get('organization_pk')
        user_pk = self.kwargs.get('user_pk')
        queryset = UserOrganizationRole.objects.all()

        if organization_pk:
            queryset = queryset.filter(organization__pk=organization_pk)
            self.organization = get_object_or_404(Organization, pk=organization_pk) # Store organization for context
        if user_pk:
            queryset = queryset.filter(user__pk=user_pk)
            self.target_user = get_object_or_404(CustomUser, pk=user_pk) # Store user for context

        # Optional: Filter assignments based on user's permissions (e.g., only show assignments in organizations they manage)
        # if not self.request.user.is_superuser:
        #     managed_orgs = self.request.user.get_managed_organizations() # Assuming such a method exists
        #     queryset = queryset.filter(organization__in=managed_orgs)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add organization and target_user to context if filtered
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        if hasattr(self, 'target_user'):
            context['target_user'] = self.target_user
        return context


class UserOrganizationRoleCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد انتساب نقش سازمانی جدید به کاربر.
    فقط برای کاربران مجاز قابل دسترسی است.
    """
    model = UserOrganizationRole
    form_class = UserOrganizationRoleForm
    template_name = 'users/userorganizationrole_form.html'
    success_message = "نقش سازمانی کاربر با موفقیت انتساب یافت."

    def test_func(self):
        # Only allow staff users or superusers to access this view
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_initial(self):
        """
        تنظیم مقادیر اولیه فیلدهای کاربر و سازمان بر اساس URL.
        """
        initial = super().get_initial()
        organization_pk = self.kwargs.get('organization_pk')
        user_pk = self.kwargs.get('user_pk')

        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        if user_pk:
            initial['user'] = get_object_or_404(CustomUser, pk=user_pk)

        return initial

    def get_form_kwargs(self):
        """
        ارسال شیء سازمان به فرم برای فیلتر کردن نقش‌ها.
        """
        kwargs = super().get_form_kwargs()
        # Pass the organization object to the form's __init__ if available in initial data or instance
        organization = self.get_initial().get('organization') or (self.object.organization if self.object else None)
        if organization:
            kwargs['organization'] = organization
        return kwargs


    def get_success_url(self):
        """
        مسیر ریدایرکت پس از ایجاد موفقیت‌آمیز.
        ریدایرکت به لیست انتساب‌های نقش (ترجیحاً فیلتر شده بر اساس سازمان یا کاربر).
        """
        # Try to redirect to the list filtered by the organization or user of the created object
        if self.object.organization:
             return reverse_lazy('users:userorganizationrole_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        if self.object.user:
             return reverse_lazy('users:userorganizationrole_list_by_user', kwargs={'user_pk': self.object.user.pk})
        # Fallback to general list
        return reverse_lazy('users:userorganizationrole_list')


class UserOrganizationRoleUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش انتساب نقش سازمانی به کاربر.
    فقط برای کاربران مجاز قابل دسترسی است.
    """
    model = UserOrganizationRole
    form_class = UserOrganizationRoleForm
    template_name = 'users/userorganizationrole_form.html'
    context_object_name = 'user_organization_role'
    success_message = "انتساب نقش سازمانی کاربر با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Only allow staff users or superusers to access this view
        # You might also want to check if the user has permission to manage roles in this specific organization
        # return self.request.user.is_staff or self.request.user.is_superuser and self.request.user.can_manage_organization_roles(self.get_object().organization)
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_form_kwargs(self):
        """
        ارسال شیء سازمان به فرم برای فیلتر کردن نقش‌ها.
        """
        kwargs = super().get_form_kwargs()
        # Pass the organization object from the instance to the form's __init__
        if self.object.organization:
            kwargs['organization'] = self.object.organization
        return kwargs


    def get_success_url(self):
        """
        مسیر ریدایرکت پس از ویرایش موفقیت‌آمیز.
        ریدایرکت به لیست انتساب‌های نقش (ترجیحاً فیلتر شده بر اساس سازمان یا کاربر مرتبط با انتساب).
        """
        # Get organization or user from the object being updated
        if self.object.organization:
             return reverse_lazy('users:userorganizationrole_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        if self.object.user:
             return reverse_lazy('users:userorganizationrole_list_by_user', kwargs={'user_pk': self.object.user.pk})
        # Fallback to general list
        return reverse_lazy('users:userorganizationrole_list')


class UserOrganizationRoleDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف انتساب نقش سازمانی به کاربر.
    فقط برای کاربران مجاز قابل دسترسی است.
    """
    model = UserOrganizationRole
    template_name = 'users/userorganizationrole_confirm_delete.html'
    context_object_name = 'user_organization_role'
    success_message = "انتساب نقش سازمانی کاربر با موفقیت حذف شد."

    def test_func(self):
        # Only allow staff users or superusers to access this view
        # You might also want to check if the user has permission to manage roles in this specific organization
        # return self.request.user.is_staff or self.request.user.is_superuser and self.request.user.can_manage_organization_roles(self.get_object().organization)
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_success_url(self):
        """
        مسیر ریدایرکت پس از حذف موفقیت‌آمیز.
        ریدایرکت به لیست انتساب‌های نقش (ترجیحاً فیلتر شده بر اساس سازمان یا کاربر مرتبط با انتساب حذف شده).
        """
        # Get organization or user from the object being deleted (before it's deleted)
        if self.object.organization:
             return reverse_lazy('users:userorganizationrole_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        if self.object.user:
             return reverse_lazy('users:userorganizationrole_list_by_user', kwargs={'user_pk': self.object.user.pk})
        # Fallback to general list
        return reverse_lazy('users:userorganizationrole_list')

    # Override delete method to add success message manually
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Optional: Add Detail Views for OrganizationRole and UserOrganizationRole if needed
