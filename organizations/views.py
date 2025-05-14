from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from employees.models import Employee
from django.utils.translation import gettext as _


# import مدل‌ها و فرم‌ها
from .models import Organization, EmployeeOrganization
from .forms import OrganizationForm, EmployeeOrganizationForm

# Import CustomUser model to use has_organization_permission method
from users.models import CustomUser # Assuming CustomUser is in users.models

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


# ویوهای مدیریت سازمان‌ها (Organization)

class OrganizationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست تمامی سازمان‌ها.
    نیاز به ورود به سیستم و مجوز مشاهده سازمان‌ها دارد.
    """
    model = Organization
    template_name = 'organizations/organization_list.html'
    context_object_name = 'organizations'
    # paginate_by = 10 # اضافه کردن صفحه بندی (اختیاری)

    def test_func(self):
        # Check if the user has the general 'view_organization' permission or is staff/superuser
        # For organization-specific view permission, this needs refinement
        # A user might only be able to view organizations they are a member of or have a role in.
        # For simplicity, let's require staff/superuser or a general permission check.
        # A better approach might be to filter the queryset based on user's access.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('organizations.view_organization') # General Django permission


    def get_queryset(self):
        # Filter organizations based on user's access (e.g., organizations they are a member of or manage)
        # This requires implementing methods on the CustomUser model to get accessible organizations.
        # For now, let's return all organizations for staff/superuser, or filter based on membership for others.
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Organization.objects.all()
        else:
            # Show only organizations the user is a member of
            user_org_ids = self.request.user.user_organization_roles.values_list('organization', flat=True)
            return Organization.objects.filter(pk__in=user_org_ids)


class OrganizationCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد سازمان جدید.
    نیاز به ورود به سیستم و مجوز افزودن سازمان دارد.
    """
    model = Organization
    form_class = OrganizationForm
    template_name = 'organizations/organization_form.html'
    success_url = reverse_lazy('organizations:organization_list')
    success_message = "سازمان با موفقیت ایجاد شد."

    def test_func(self):
        # Only allow users with 'add_organization' permission or staff/superuser
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('organizations.add_organization')


class OrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش سازمان موجود.
    نیاز به ورود به سیستم و مجوز تغییر سازمان (در آن سازمان) دارد.
    """
    model = Organization
    form_class = OrganizationForm
    template_name = 'organizations/organization_form.html'
    context_object_name = 'organization'
    success_message = "سازمان با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_organization' permission in this specific organization
        organization = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, organization, 'organizations.change_organization')

    def get_success_url(self):
        return reverse_lazy('organizations:organization_list')


class OrganizationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    حذف سازمان.
    نیاز به ورود به سیستم و مجوز حذف سازمان (در آن سازمان) دارد.
    """
    model = Organization
    template_name = 'organizations/organization_confirm_delete.html'
    success_url = reverse_lazy('organizations:organization_list')
    context_object_name = 'organization'
    success_message = "سازمان با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_organization' permission in this specific organization
        organization = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, organization, 'organizations.delete_organization')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response

# ویوهای مدیریت عضویت کارمند در سازمان (EmployeeOrganization)

class EmployeeOrganizationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست عضویت‌های کارمندان در سازمان‌ها.
    نیاز به ورود به سیستم و مجوز مشاهده عضویت‌ها دارد.
    می‌تواند فیلتر بر اساس سازمان یا کارمند داشته باشد.
    """
    model = EmployeeOrganization
    template_name = 'organizations/employeeorganization_list.html'
    context_object_name = 'employee_organizations'
    # paginate_by = 10 # اضافه کردن صفحه بندی (اختیاری)

    def test_func(self):
        # Check if the user has the general 'view_employeeorganization' permission or is staff/superuser
        # For organization-specific view permission, this needs refinement
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('organizations.view_employeeorganization')


    def get_queryset(self):
        # Filter memberships based on user's access to the organization or employee
        organization_pk = self.kwargs.get('organization_pk')
        employee_pk = self.kwargs.get('employee_pk')
        queryset = EmployeeOrganization.objects.all()

        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view memberships in this organization
            if not has_org_permission(self.request.user, organization, 'organizations.view_employeeorganization'):
                 # If no permission, return empty queryset or raise exception
                 messages.error(self.request, _("شما مجوز مشاهده عضویت‌ها در این سازمان را ندارید."))
                 return EmployeeOrganization.objects.none() # Return empty

            queryset = queryset.filter(organization=organization)
            self.organization = organization # Store for context

        if employee_pk:
            employee = get_object_or_404(Employee, pk=employee_pk)
            # Check if user has permission to view memberships for this employee (might be complex)
            # For simplicity, let's assume if they can view the employee, they can view their memberships
            # This requires checking permission in any organization the employee belongs to.
            user_can_view_employee = False
            for emp_org in employee.employee_organizations.all():
                 if has_org_permission(self.request.user, emp_org.organization, 'employees.view_employee'):
                     user_can_view_employee = True
                     break
            if not user_can_view_employee and not self.request.user.is_staff and not self.request.user.is_superuser:
                 messages.error(self.request, _("شما مجوز مشاهده عضویت‌های این کارمند را ندارید."))
                 return EmployeeOrganization.objects.none()

            queryset = queryset.filter(employee=employee)
            self.employee = employee # Store for context

        # If no specific filter, show only memberships in organizations the user has permission to view
        if not organization_pk and not employee_pk and not self.request.user.is_staff and not self.request.user.is_superuser:
             user_org_ids = self.request.user.user_organization_roles.values_list('organization', flat=True)
             queryset = queryset.filter(organization__in=user_org_ids)
             # Note: This might still show memberships for employees the user cannot view directly.
             # A more robust check is needed for complex scenarios.


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        if hasattr(self, 'employee'):
            context['employee'] = self.employee
        return context


class EmployeeOrganizationCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد عضویت جدید کارمند در سازمان.
    نیاز به ورود به سیستم و مجوز افزودن عضویت (در سازمان مربوطه) دارد.
    """
    model = EmployeeOrganization
    form_class = EmployeeOrganizationForm
    template_name = 'organizations/employeeorganization_form.html'
    success_url = reverse_lazy('organizations:employeeorganization_list')
    success_message = "عضویت کارمند در سازمان با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the 'add_employeeorganization' permission
        # This permission check should ideally be organization-specific.
        # If organization is passed in URL, check permission in that organization.
        # If not, a general permission check or checking permission in all user's orgs is needed.
        # For simplicity, let's require staff/superuser or a general permission check for now.
        # A better approach is to get the organization from initial data or form and check permission there.
        # Example if organization_pk is in URL:
        # organization_pk = self.kwargs.get('organization_pk')
        # if organization_pk:
        #      organization = get_object_or_404(Organization, pk=organization_pk)
        #      return self.request.user.is_staff or self.request.user.is_superuser or \
        #             has_org_permission(self.request.user, organization, 'organizations.add_employeeorganization')
        # Fallback for general create page:
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('organizations.add_employeeorganization')


    def get_initial(self):
        """
        Set initial data for employee and organization from URL if available.
        """
        initial = super().get_initial()
        organization_pk = self.kwargs.get('organization_pk')
        employee_pk = self.kwargs.get('employee_pk')

        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        if employee_pk:
            initial['employee'] = get_object_or_404(Employee, pk=employee_pk)

        return initial

    def form_valid(self, form):
        # Check organization-specific permission before saving if organization is in the form
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'organizations.add_employeeorganization'):
                 messages.error(self.request, _("شما مجوز افزودن عضویت در این سازمان را ندارید."))
                 return self.form_invalid(form) # Return invalid form with error message

        return super().form_valid(form)


class EmployeeOrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش عضویت کارمند در سازمان.
    نیاز به ورود به سیستم و مجوز تغییر عضویت (در سازمان مربوطه) دارد.
    """
    model = EmployeeOrganization
    form_class = EmployeeOrganizationForm
    template_name = 'organizations/employeeorganization_form.html'
    context_object_name = 'employee_organization'
    success_message = "عضویت کارمند در سازمان با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_employeeorganization' permission in the organization of the membership
        membership = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, membership.organization, 'organizations.change_employeeorganization')

    def get_success_url(self):
        return reverse_lazy('organizations:employeeorganization_list')


class EmployeeOrganizationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    حذف عضویت کارمند در سازمان.
    نیاز به ورود به سیستم و مجوز حذف عضویت (در سازمان مربوطه) دارد.
    """
    model = EmployeeOrganization
    template_name = 'organizations/employeeorganization_confirm_delete.html'
    success_url = reverse_lazy('organizations:employeeorganization_list')
    context_object_name = 'employee_organization'
    success_message = "عضویت کارمند در سازمان با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_employeeorganization' permission in the organization of the membership
        membership = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, membership.organization, 'organizations.delete_employeeorganization')


    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response

# Optional: Add Detail Views for any of the models if needed.
