from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q

# Import models and forms from the current app
from .models import SalaryItemType, EmployeeSalaryItem
from .forms import SalaryItemTypeForm, EmployeeSalaryItemForm

# Import necessary models from other apps for filtering or context
from organizations.models import Organization
from employees.models import Employee
from settings_app.models import FinancialPeriod

# Import CustomUser model for permission checks
from users.models import CustomUser # Assuming CustomUser is in users.models
from django.utils.translation import gettext as _


# Helper function to check organization-specific permission (can be defined in users app and imported)
def has_org_permission(user, organization, perm_name):
    """
    Checks if the user has the specified permission in the given organization.
    Assumes user is an instance of CustomUser with the has_organization_permission method.
    """
    if not isinstance(user, CustomUser):
        # Handle cases where user is not CustomUser (e.g., AnonymousUser)
        return False
    return user.has_organization_permission(organization, perm_name)


# --- Views for SalaryItemType (Management of Salary Item Types) ---

class SalaryItemTypeList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست انواع آیتم‌های حقوقی.
    نیاز به ورود به سیستم و مجوز مشاهده انواع آیتم‌های حقوقی (در سازمان مربوطه) دارد.
    می‌تواند فیلتر بر اساس سازمان یا دوره مالی داشته باشد.
    """
    model = SalaryItemType
    template_name = 'salaries/salaryitemtype_list.html'
    context_object_name = 'salary_item_types'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the general 'view_salaryitemtype' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('salaries.view_salaryitemtype')


    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')

        queryset = SalaryItemType.objects.all()

        # Filter by organization first if available
        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view salary item types in this organization
            if not has_org_permission(self.request.user, organization, 'salaries.view_salaryitemtype'):
                 messages.error(self.request, _("شما مجوز مشاهده انواع آیتم‌های حقوقی در این سازمان را ندارید."))
                 return SalaryItemType.objects.none()

            queryset = queryset.filter(organization=organization)
            self.organization = organization # Store organization for context

            # Apply financial period filter within this organization
            if financial_period_pk:
                queryset = queryset.filter(financial_period__pk=financial_period_pk)
                self.financial_period = get_object_or_404(FinancialPeriod, pk=financial_period_pk)

        elif financial_period_pk:
             # Handle cases where organization is not in URL but period is
             # This is more complex as we need to check permission for the organization
             # the period belongs to.
             # For simplicity, let's require organization_pk for filtered lists for now.
             messages.warning(self.request, _("لطفاً سازمان مورد نظر را برای مشاهده انواع آیتم‌های حقوقی انتخاب کنید."))
             return SalaryItemType.objects.none()

        else:
            # If no specific filter, show only types in organizations the user has permission to view them in
            user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'salaries.view_salaryitemtype')
            ]
            queryset = queryset.filter(organization__pk__in=user_accessible_org_ids)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        if hasattr(self, 'financial_period'):
            context['financial_period'] = self.financial_period
        return context


class SalaryItemTypeCreate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد نوع آیتم حقوقی جدید.
    نیاز به ورود به سیستم و مجوز افزودن نوع آیتم حقوقی (در سازمان مربوطه) دارد.
    """
    model = SalaryItemType
    form_class = SalaryItemTypeForm
    template_name = 'salaries/salaryitemtype_form.html'
    success_message = "نوع آیتم حقوقی با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_salaryitemtype' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('salaries.add_salaryitemtype')

    def get_initial(self):
        initial = super().get_initial()
        organization_pk = self.kwargs.get('organization_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')

        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        if financial_period_pk:
            initial['financial_period'] = get_object_or_404(FinancialPeriod, pk=financial_period_pk)

        return initial

    def form_valid(self, form):
        # Check organization-specific permission before saving based on the selected organization
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'salaries.add_salaryitemtype'):
                 messages.error(self.request, _("شما مجوز افزودن نوع آیتم حقوقی در این سازمان را ندارید."))
                 return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        organization_pk = self.object.organization.pk
        financial_period_pk = self.object.financial_period.pk
        return reverse_lazy('salaries:salaryitemtype_list', kwargs={'organization_pk': organization_pk, 'financial_period_pk': financial_period_pk})


class SalaryItemTypeUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش نوع آیتم حقوقی موجود.
    نیاز به ورود به سیستم و مجوز تغییر نوع آیتم حقوقی (در سازمان مربوطه) دارد.
    """
    model = SalaryItemType
    form_class = SalaryItemTypeForm
    template_name = 'salaries/salaryitemtype_form.html'
    context_object_name = 'salary_item_type'
    success_message = "نوع آیتم حقوقی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_salaryitemtype' permission in the organization of the salary item type
        item_type = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, item_type.organization, 'salaries.change_salaryitemtype')


    def get_success_url(self):
        organization_pk = self.object.organization.pk
        financial_period_pk = self.object.financial_period.pk
        return reverse_lazy('salaries:salaryitemtype_list', kwargs={'organization_pk': organization_pk, 'financial_period_pk': financial_period_pk})


class SalaryItemTypeDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف نوع آیتم حقوقی.
    نیاز به ورود به سیستم و مجوز حذف نوع آیتم حقوقی (در سازمان مربوطه) دارد.
    """
    model = SalaryItemType
    template_name = 'salaries/salaryitemtype_confirm_delete.html'
    context_object_name = 'salary_item_type'
    success_message = "نوع آیتم حقوقی با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_salaryitemtype' permission in the organization of the salary item type
        item_type = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, item_type.organization, 'salaries.delete_salaryitemtype')

    def get_success_url(self):
        organization_pk = self.object.organization.pk
        financial_period_pk = self.object.financial_period.pk
        return reverse_lazy('salaries:salaryitemtype_list', kwargs={'organization_pk': organization_pk, 'financial_period_pk': financial_period_pk})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# --- Views for EmployeeSalaryItem (Management of Employee Salary Items) ---

class EmployeeSalaryItemListByEmployee(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست آیتم‌های حقوقی برای یک کارمند خاص در یک دوره مالی خاص.
    نیاز به ورود به سیستم و مجوز مشاهده آیتم‌های حقوقی کارمند (در سازمان مربوطه) دارد.
    """
    model = EmployeeSalaryItem
    template_name = 'salaries/employeesalaryitem_list_by_employee.html'
    context_object_name = 'employee_salary_items'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the 'view_employeesalaryitem' permission in the organization of the financial period
        financial_period = get_object_or_404(FinancialPeriod, pk=self.kwargs['financial_period_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, financial_period.organization, 'salaries.view_employeesalaryitem')


    def get_queryset(self):
        employee_pk = self.kwargs.get('employee_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')

        self.employee = get_object_or_404(Employee, pk=employee_pk)
        self.financial_period = get_object_or_404(FinancialPeriod, pk=financial_period_pk)

        # Check if the employee is associated with the organization of the financial period
        # This is a sanity check, data integrity should ideally prevent this mismatch
        if not self.employee.employee_organizations.filter(organization=self.financial_period.organization).exists():
             messages.error(self.request, _("کارمند مورد نظر به سازمان مرتبط با این دوره مالی تعلق ندارد."))
             return EmployeeSalaryItem.objects.none() # Return empty queryset

        queryset = EmployeeSalaryItem.objects.filter(
            employee=self.employee,
            financial_period=self.financial_period
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        context['financial_period'] = self.financial_period
        context['organization'] = self.financial_period.organization # Add organization to context
        return context


class EmployeeSalaryItemCreate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد آیتم حقوقی جدید برای کارمند در یک دوره مالی.
    نیاز به ورود به سیستم و مجوز افزودن آیتم حقوقی کارمند (در سازمان مربوطه) دارد.
    """
    model = EmployeeSalaryItem
    form_class = EmployeeSalaryItemForm
    template_name = 'salaries/employeesalaryitem_form.html'
    success_message = "آیتم حقوقی کارمند با موفقیت اضافه شد."

    def test_func(self):
        # Check if the user has the 'add_employeesalaryitem' permission in the organization of the financial period
        financial_period = get_object_or_404(FinancialPeriod, pk=self.kwargs['financial_period_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, financial_period.organization, 'salaries.add_employeesalaryitem')

    def get_initial(self):
        initial = super().get_initial()
        employee_pk = self.kwargs.get('employee_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')

        if employee_pk:
            initial['employee'] = get_object_or_404(Employee, pk=employee_pk)
        if financial_period_pk:
            initial['financial_period'] = get_object_or_404(FinancialPeriod, pk=financial_period_pk)

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass organization and financial period to the form's __init__ for filtering salary item types
        financial_period = self.get_initial().get('financial_period') or (self.object.financial_period if self.object else None)
        if financial_period:
            kwargs['financial_period'] = financial_period
            kwargs['organization'] = financial_period.organization # Pass organization as well
        return kwargs


    def form_valid(self, form):
        # Assign employee and financial period from URL kwargs
        employee = get_object_or_404(Employee, pk=self.kwargs['employee_pk'])
        financial_period = get_object_or_404(FinancialPeriod, pk=self.kwargs['financial_period_pk'])

        form.instance.employee = employee
        form.instance.financial_period = financial_period

        # Check if the employee is associated with the organization of the financial period
        if not employee.employee_organizations.filter(organization=financial_period.organization).exists():
             messages.error(self.request, _("کارمند مورد نظر به سازمان مرتبط با این دوره مالی تعلق ندارد."))
             return self.form_invalid(form) # Return invalid form with error message


        return super().form_valid(form)

    def get_success_url(self):
        employee_pk = self.kwargs.get('employee_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')
        return reverse_lazy('salaries:employeesalaryitem_list_by_employee', kwargs={'employee_pk': employee_pk, 'financial_period_pk': financial_period_pk})


class EmployeeSalaryItemUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش آیتم حقوقی کارمند موجود.
    نیاز به ورود به سیستم و مجوز تغییر آیتم حقوقی کارمند (در سازمان مربوطه) دارد.
    """
    model = EmployeeSalaryItem
    form_class = EmployeeSalaryItemForm
    template_name = 'salaries/employeesalaryitem_form.html'
    context_object_name = 'employee_salary_item'
    success_message = "آیتم حقوقی کارمند با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_employeesalaryitem' permission in the organization of the financial period
        item = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, item.financial_period.organization, 'salaries.change_employeesalaryitem')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass organization and financial period from the instance to the form's __init__
        kwargs['financial_period'] = self.object.financial_period
        kwargs['organization'] = self.object.financial_period.organization
        return kwargs


    def get_success_url(self):
        employee_pk = self.object.employee.pk
        financial_period_pk = self.object.financial_period.pk
        return reverse_lazy('salaries:employeesalaryitem_list_by_employee', kwargs={'employee_pk': employee_pk, 'financial_period_pk': financial_period_pk})


class EmployeeSalaryItemDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف آیتم حقوقی کارمند.
    نیاز به ورود به سیستم و مجوز حذف آیتم حقوقی کارمند (در سازمان مربوطه) دارد.
    """
    model = EmployeeSalaryItem
    template_name = 'salaries/employeesalaryitem_confirm_delete.html'
    context_object_name = 'employee_salary_item'
    success_message = "آیتم حقوقی کارمند با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_employeesalaryitem' permission in the organization of the financial period
        item = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, item.financial_period.organization, 'salaries.delete_employeesalaryitem')

    def get_success_url(self):
        employee_pk = self.object.employee.pk
        financial_period_pk = self.object.financial_period.pk
        return reverse_lazy('salaries:employeesalaryitem_list_by_employee', kwargs={'employee_pk': employee_pk, 'financial_period_pk': financial_period_pk})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Note: Detail Views can be added for both models if needed.
