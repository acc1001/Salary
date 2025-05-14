from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import (
    ListView,
    DetailView, # Optional: Add DetailView if needed
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

# Import models and forms from the current app
from .models import EmployeeLoan
from .forms import EmployeeLoanForm

# Import necessary models from other apps for filtering or context
from employees.models import Employee
from organizations.models import Organization

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


# --- Views for EmployeeLoan ---

class EmployeeLoanListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست وام‌های کارکنان.
    نیاز به ورود به سیستم و مجوز مشاهده وام‌ها (در سازمان مربوطه) دارد.
    می‌تواند فیلتر بر اساس کارمند یا سازمان داشته باشد.
    """
    model = EmployeeLoan
    template_name = 'loans/employeeloan_list.html'
    context_object_name = 'employee_loans'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the general 'view_employeeloan' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('loans.view_employeeloan')


    def get_queryset(self):
        employee_pk = self.kwargs.get('employee_pk')
        organization_pk = self.kwargs.get('organization_pk')

        queryset = EmployeeLoan.objects.all()

        # Filter by organization first if available
        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view loans in this organization
            if not has_org_permission(self.request.user, organization, 'loans.view_employeeloan'):
                 messages.error(self.request, _("شما مجوز مشاهده وام‌ها در این سازمان را ندارید."))
                 return EmployeeLoan.objects.none()

            queryset = queryset.filter(organization=organization)
            self.organization = organization # Store organization for context

            # Apply employee filter within this organization
            if employee_pk:
                queryset = queryset.filter(employee__pk=employee_pk)
                self.employee = get_object_or_404(Employee, pk=employee_pk)

        elif employee_pk:
             # Handle cases where organization is not in URL but employee is
             # This is more complex as we need to check permission for the organization(s)
             # the employee belongs to.
             # For simplicity, let's require organization_pk for filtered lists for now.
             messages.warning(self.request, _("لطفاً سازمان مورد نظر را برای مشاهده وام‌ها انتخاب کنید."))
             return EmployeeLoan.objects.none()

        else:
            # If no specific filter, show only loans in organizations the user has permission to view them in
            user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'loans.view_employeeloan')
            ]
            queryset = queryset.filter(organization__pk__in=user_accessible_org_ids)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'employee'):
            context['employee'] = self.employee
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        return context


class EmployeeLoanCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد وام جدید برای کارمند.
    نیاز به ورود به سیستم و مجوز افزودن وام (در سازمان مربوطه) دارد.
    """
    model = EmployeeLoan
    form_class = EmployeeLoanForm
    template_name = 'loans/employeeloan_form.html'
    success_message = "وام با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_employeeloan' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('loans.add_employeeloan')

    def get_initial(self):
        initial = super().get_initial()
        employee_pk = self.kwargs.get('employee_pk')
        organization_pk = self.kwargs.get('organization_pk')

        if employee_pk:
            initial['employee'] = get_object_or_404(Employee, pk=employee_pk)
        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        organization = self.get_initial().get('organization') or (self.object.organization if self.object else None)
        if organization:
            kwargs['organization'] = organization
        return kwargs


    def form_valid(self, form):
        # Check organization-specific permission before saving based on the selected organization
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'loans.add_employeeloan'):
                 messages.error(self.request, _("شما مجوز افزودن وام در این سازمان را ندارید."))
                 return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employee:
            return reverse_lazy('loans:employeeloan_list_by_employee', kwargs={'employee_pk': self.object.employee.pk})
        if self.object.organization:
            return reverse_lazy('loans:employeeloan_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        return reverse_lazy('loans:employeeloan_list')


class EmployeeLoanUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش وام موجود.
    نیاز به ورود به سیستم و مجوز تغییر وام (در سازمان مربوطه) دارد.
    """
    model = EmployeeLoan
    form_class = EmployeeLoanForm
    template_name = 'loans/employeeloan_form.html'
    context_object_name = 'employee_loan'
    success_message = "وام با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_employeeloan' permission in the organization of the loan
        loan = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, loan.organization, 'loans.change_employeeloan')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object.organization:
            kwargs['organization'] = self.object.organization
        return kwargs


    def get_success_url(self):
        employee_pk = self.object.employee.pk
        return reverse_lazy('loans:employeeloan_list_by_employee', kwargs={'employee_pk': employee_pk})


class EmployeeLoanDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف وام.
    نیاز به ورود به سیستم و مجوز حذف وام (در سازمان مربوطه) دارد.
    """
    model = EmployeeLoan
    template_name = 'loans/employeeloan_confirm_delete.html'
    context_object_name = 'employee_loan'
    success_message = "وام با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_employeeloan' permission in the organization of the loan
        loan = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, loan.organization, 'loans.delete_employeeloan')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Note: Add DetailView and corresponding permission checks when implemented.
