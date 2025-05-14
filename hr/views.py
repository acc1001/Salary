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
from django.db.models import Q

# Import models and forms from the current app
from .models import Department, JobTitle, EmploymentHistory, MonthlyWorkRecord
from .forms import DepartmentForm, JobTitleForm, EmploymentHistoryForm, MonthlyWorkRecordForm

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


# --- Views for Department ---

class DepartmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست دپارتمان‌ها.
    نیاز به ورود به سیستم و مجوز مشاهده دپارتمان‌ها (در سازمان مربوطه) دارد.
    می‌تواند فیلتر بر اساس سازمان داشته باشد.
    """
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'department_list'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the general 'view_department' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.view_department')


    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk')
        queryset = Department.objects.all()

        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view departments in this organization
            if not has_org_permission(self.request.user, organization, 'hr.view_department'):
                 messages.error(self.request, _("شما مجوز مشاهده دپارتمان‌ها در این سازمان را ندارید."))
                 return Department.objects.none() # Return empty

            queryset = queryset.filter(organization=organization)
            self.organization = organization # Store organization for context
        else:
            # If no organization_pk, show only departments in organizations the user has permission to view them in
            # This requires defining what "permission to view departments in an organization" means.
            # Let's assume it means having 'hr.view_department' permission in that organization.
            user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'hr.view_department')
            ]
            queryset = queryset.filter(organization__pk__in=user_accessible_org_ids)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        return context


class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد دپارتمان جدید.
    نیاز به ورود به سیستم و مجوز افزودن دپارتمان (در سازمان مربوطه) دارد.
    """
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_message = "دپارتمان با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_department' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.add_department')

    def get_initial(self):
        initial = super().get_initial()
        organization_pk = self.kwargs.get('organization_pk')
        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        return initial

    def form_valid(self, form):
        # Check organization-specific permission before saving based on the selected organization
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'hr.add_department'):
                 messages.error(self.request, _("شما مجوز افزودن دپارتمان در این سازمان را ندارید."))
                 return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        if self.object.organization:
             return reverse_lazy('hr:department_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        return reverse_lazy('hr:department_list')


class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش دپارتمان موجود.
    نیاز به ورود به سیستم و مجوز تغییر دپارتمان (در سازمان مربوطه) دارد.
    """
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    context_object_name = 'department'
    success_message = "دپارتمان با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_department' permission in the organization of the department
        department = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, department.organization, 'hr.change_department')

    def get_success_url(self):
        organization_pk = self.object.organization.pk
        return reverse_lazy('hr:department_list_by_org', kwargs={'organization_pk': organization_pk})


class DepartmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف دپارتمان.
    نیاز به ورود به سیستم و مجوز حذف دپارتمان (در سازمان مربوطه) دارد.
    """
    model = Department
    template_name = 'hr/department_confirm_delete.html'
    context_object_name = 'department'
    success_message = "دپارتمان با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_department' permission in the organization of the department
        department = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, department.organization, 'hr.delete_department')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# --- Views for JobTitle ---

class JobTitleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست عناوین شغلی.
    نیاز به ورود به سیستم و مجوز مشاهده عناوین شغلی (در سازمان مربوطه) دارد.
    می‌تواند فیلتر بر اساس سازمان داشته باشد.
    """
    model = JobTitle
    template_name = 'hr/jobtitle_list.html'
    context_object_name = 'jobtitle_list'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the general 'view_jobtitle' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.view_jobtitle')


    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk')
        queryset = JobTitle.objects.all()

        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view job titles in this organization
            if not has_org_permission(self.request.user, organization, 'hr.view_jobtitle'):
                 messages.error(self.request, _("شما مجوز مشاهده عناوین شغلی در این سازمان را ندارید."))
                 return JobTitle.objects.none() # Return empty

            # Filter by specific organization or job titles with no organization (general)
            queryset = queryset.filter(Q(organization__pk=organization_pk) | Q(organization__isnull=True))
            self.organization = organization # Store organization for context
        else:
            # If no organization_pk, show only job titles in organizations the user has permission to view them in
            # and general job titles (organization__isnull=True).
            user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'hr.view_jobtitle')
            ]
            queryset = queryset.filter(Q(organization__pk__in=user_accessible_org_ids) | Q(organization__isnull=True))


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        return context


class JobTitleCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد عنوان شغلی جدید.
    نیاز به ورود به سیستم و مجوز افزودن عنوان شغلی (در سازمان مربوطه) دارد.
    """
    model = JobTitle
    form_class = JobTitleForm
    template_name = 'hr/jobtitle_form.html'
    success_message = "عنوان شغلی با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_jobtitle' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.add_jobtitle')


    def get_initial(self):
        initial = super().get_initial()
        organization_pk = self.kwargs.get('organization_pk')
        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        return initial

    def form_valid(self, form):
        # Check organization-specific permission before saving based on the selected organization
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'hr.add_jobtitle'):
                 messages.error(self.request, _("شما مجوز افزودن عنوان شغلی در این سازمان را ندارید."))
                 return self.form_invalid(form)
        # If organization is None (general job title), check general permission (already done in test_func)

        return super().form_valid(form)

    def get_success_url(self):
        organization_pk = self.object.organization.pk if self.object.organization else None
        if organization_pk:
             return reverse_lazy('hr:jobtitle_list_by_org', kwargs={'organization_pk': organization_pk})
        return reverse_lazy('hr:jobtitle_list')


class JobTitleUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش عنوان شغلی موجود.
    نیاز به ورود به سیستم و مجوز تغییر عنوان شغلی (در سازمان مربوطه) دارد.
    """
    model = JobTitle
    form_class = JobTitleForm
    template_name = 'hr/jobtitle_form.html'
    context_object_name = 'jobtitle'
    success_message = "عنوان شغلی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_jobtitle' permission in the organization of the job title (if any)
        job_title = self.get_object()
        if job_title.organization:
            return self.request.user.is_staff or self.request.user.is_superuser or \
                   has_org_permission(self.request.user, job_title.organization, 'hr.change_jobtitle')
        else:
            # For general job titles, require general permission or staff/superuser
            return self.request.user.is_staff or self.request.user.is_superuser or \
                   self.request.user.has_perm('hr.change_jobtitle')


    def get_success_url(self):
        organization_pk = self.object.organization.pk if self.object.organization else None
        if organization_pk:
             return reverse_lazy('hr:jobtitle_list_by_org', kwargs={'organization_pk': organization_pk})
        return reverse_lazy('hr:jobtitle_list')


class JobTitleDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف عنوان شغلی.
    نیاز به ورود به سیستم و مجوز حذف عنوان شغلی (در سازمان مربوطه) دارد.
    """
    model = JobTitle
    template_name = 'hr/jobtitle_confirm_delete.html'
    context_object_name = 'jobtitle'
    success_message = "عنوان شغلی با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_jobtitle' permission in the organization of the job title (if any)
        job_title = self.get_object()
        if job_title.organization:
            return self.request.user.is_staff or self.request.user.is_superuser or \
                   has_org_permission(self.request.user, job_title.organization, 'hr.delete_jobtitle')
        else:
            # For general job titles, require general permission or staff/superuser
            return self.request.user.is_staff or self.request.user.is_superuser or \
                   self.request.user.has_perm('hr.delete_jobtitle')


    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# --- Views for EmploymentHistory ---

class EmploymentHistoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست سوابق شغلی.
    نیاز به ورود به سیستم و مجوز مشاهده سوابق شغلی (در سازمان مربوطه) دارد.
    می‌تواند فیلتر بر اساس کارمند یا سازمان داشته باشد.
    """
    model = EmploymentHistory
    template_name = 'hr/employmenthistory_list.html'
    context_object_name = 'employmenthistory_list'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the general 'view_employmenthistory' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.view_employmenthistory')


    def get_queryset(self):
        employee_pk = self.kwargs.get('employee_pk')
        organization_pk = self.kwargs.get('organization_pk')

        queryset = EmploymentHistory.objects.all()

        if employee_pk:
            employee = get_object_or_404(Employee, pk=employee_pk)
            # Check if user has permission to view this employee's history in any of their organizations
            user_can_view_history = False
            for emp_org in employee.employee_organizations.all():
                 if has_org_permission(self.request.user, emp_org.organization, 'hr.view_employmenthistory'):
                     user_can_view_history = True
                     break
            if not user_can_view_history and not self.request.user.is_staff and not self.request.user.is_superuser:
                 messages.error(self.request, _("شما مجوز مشاهده سوابق شغلی این کارمند را ندارید."))
                 return EmploymentHistory.objects.none()

            queryset = queryset.filter(employee=employee)
            self.employee = employee # Store employee for context

        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view history in this organization
            if not has_org_permission(self.request.user, organization, 'hr.view_employmenthistory'):
                 messages.error(self.request, _("شما مجوز مشاهده سوابق شغلی در این سازمان را ندارید."))
                 return EmploymentHistory.objects.none()

            queryset = queryset.filter(organization=organization)
            self.organization = organization # Store organization for context

        # If no specific filter, show only history in organizations the user has permission to view them in
        if not employee_pk and not organization_pk and not self.request.user.is_staff and not self.request.user.is_superuser:
             user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'hr.view_employmenthistory')
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


class EmploymentHistoryCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد سابقه شغلی جدید.
    نیاز به ورود به سیستم و مجوز افزودن سابقه شغلی (در سازمان مربوطه) دارد.
    """
    model = EmploymentHistory
    form_class = EmploymentHistoryForm
    template_name = 'hr/employmenthistory_form.html'
    success_message = "سابقه شغلی با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_employmenthistory' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.add_employmenthistory')

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
            if not has_org_permission(self.request.user, organization, 'hr.add_employmenthistory'):
                 messages.error(self.request, _("شما مجوز افزودن سابقه شغلی در این سازمان را ندارید."))
                 return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employee:
             return reverse_lazy('hr:employmenthistory_list_by_employee', kwargs={'employee_pk': self.object.employee.pk})
        if self.object.organization:
             return reverse_lazy('hr:employmenthistory_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        return reverse_lazy('hr:employmenthistory_list')


class EmploymentHistoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش سابقه شغلی موجود.
    نیاز به ورود به سیستم و مجوز تغییر سابقه شغلی (در سازمان مربوطه) دارد.
    """
    model = EmploymentHistory
    form_class = EmploymentHistoryForm
    template_name = 'hr/employmenthistory_form.html'
    context_object_name = 'employmenthistory'
    success_message = "سابقه شغلی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_employmenthistory' permission in the organization of the history entry
        history = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, history.organization, 'hr.change_employmenthistory')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object.organization:
            kwargs['organization'] = self.object.organization
        return kwargs


    def get_success_url(self):
        employee_pk = self.object.employee.pk
        return reverse_lazy('hr:employmenthistory_list_by_employee', kwargs={'employee_pk': employee_pk})


class EmploymentHistoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف سابقه شغلی.
    نیاز به ورود به سیستم و مجوز حذف سابقه شغلی (در سازمان مربوطه) دارد.
    """
    model = EmploymentHistory
    template_name = 'hr/employmenthistory_confirm_delete.html'
    context_object_name = 'employmenthistory'
    success_message = "سابقه شغلی با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_employmenthistory' permission in the organization of the history entry
        history = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, history.organization, 'hr.delete_employmenthistory')


    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# --- Views for MonthlyWorkRecord ---

class MonthlyWorkRecordListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست رکوردهای کارکرد ماهیانه.
    نیاز به ورود به سیستم و مجوز مشاهده رکوردهای کارکرد (در سازمان مربوطه) دارد.
    می‌تواند فیلتر بر اساس کارمند، سازمان یا دوره مالی داشته باشد.
    """
    model = MonthlyWorkRecord
    template_name = 'hr/monthlyworkrecord_list.html'
    context_object_name = 'monthlyworkrecord_list'
    # paginate_by = 10

    def test_func(self):
        # Check if the user has the general 'view_monthlyworkrecord' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.view_monthlyworkrecord')


    def get_queryset(self):
        employee_pk = self.kwargs.get('employee_pk')
        organization_pk = self.kwargs.get('organization_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')

        queryset = MonthlyWorkRecord.objects.all()

        # Filter by organization first if available
        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)
            # Check if user has permission to view work records in this organization
            if not has_org_permission(self.request.user, organization, 'hr.view_monthlyworkrecord'):
                 messages.error(self.request, _("شما مجوز مشاهده رکوردهای کارکرد در این سازمان را ندارید."))
                 return MonthlyWorkRecord.objects.none()

            queryset = queryset.filter(organization=organization)
            self.organization = organization # Store organization for context

            # Apply employee and financial period filters within this organization
            if employee_pk:
                queryset = queryset.filter(employee__pk=employee_pk)
                self.employee = get_object_or_404(Employee, pk=employee_pk)
            if financial_period_pk:
                queryset = queryset.filter(financial_period__pk=financial_period_pk)
                self.financial_period = get_object_or_404(FinancialPeriod, pk=financial_period_pk)

        elif employee_pk or financial_period_pk:
             # Handle cases where organization is not in URL but employee or period is
             # This is more complex as we need to check permission for the organization(s)
             # the employee/period belongs to.
             # For simplicity, let's require organization_pk for filtered lists for now.
             messages.warning(self.request, _("لطفاً سازمان مورد نظر را برای مشاهده رکوردهای کارکرد انتخاب کنید."))
             return MonthlyWorkRecord.objects.none()

        else:
            # If no specific filter, show only work records in organizations the user has permission to view them in
            user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'hr.view_monthlyworkrecord')
            ]
            queryset = queryset.filter(organization__pk__in=user_accessible_org_ids)


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'employee'):
            context['employee'] = self.employee
        if hasattr(self, 'organization'):
            context['organization'] = self.organization
        if hasattr(self, 'financial_period'):
            context['financial_period'] = self.financial_period
        return context


class MonthlyWorkRecordCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد رکورد کارکرد ماهیانه جدید.
    نیاز به ورود به سیستم و مجوز افزودن رکورد کارکرد (در سازمان مربوطه) دارد.
    """
    model = MonthlyWorkRecord
    form_class = MonthlyWorkRecordForm
    template_name = 'hr/monthlyworkrecord_form.html'
    success_message = "رکورد کارکرد ماهیانه با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_monthlyworkrecord' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('hr.add_monthlyworkrecord')

    def get_initial(self):
        initial = super().get_initial()
        employee_pk = self.kwargs.get('employee_pk')
        organization_pk = self.kwargs.get('organization_pk')
        financial_period_pk = self.kwargs.get('financial_period_pk')

        if employee_pk:
            initial['employee'] = get_object_or_404(Employee, pk=employee_pk)
        if organization_pk:
            initial['organization'] = get_object_or_404(Organization, pk=organization_pk)
        if financial_period_pk:
            initial['financial_period'] = get_object_or_404(FinancialPeriod, pk=financial_period_pk)

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        employee = self.get_initial().get('employee') or (self.object.employee if self.object else None)
        organization = self.get_initial().get('organization') or (self.object.organization if self.object else None)
        financial_period = self.get_initial().get('financial_period') or (self.object.financial_period if self.object else None)

        if employee:
            kwargs['employee'] = employee
        if organization:
            kwargs['organization'] = organization
        if financial_period:
            kwargs['financial_period'] = financial_period
        return kwargs


    def form_valid(self, form):
        # Check organization-specific permission before saving based on the selected organization
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'hr.add_monthlyworkrecord'):
                 messages.error(self.request, _("شما مجوز افزودن رکورد کارکرد در این سازمان را ندارید."))
                 return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employee and self.object.financial_period:
             return reverse_lazy('hr:monthlyworkrecord_list_by_employee_period', kwargs={'employee_pk': self.object.employee.pk, 'financial_period_pk': self.object.financial_period.pk})
        elif self.object.employee:
             return reverse_lazy('hr:monthlyworkrecord_list_by_employee', kwargs={'employee_pk': self.object.employee.pk})
        elif self.object.organization:
             return reverse_lazy('hr:monthlyworkrecord_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
        elif self.object.financial_period:
             return reverse_lazy('hr:monthlyworkrecord_list_by_period', kwargs={'financial_period_pk': self.object.financial_period.pk})
        return reverse_lazy('hr:monthlyworkrecord_list')


class MonthlyWorkRecordUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش رکورد کارکرد ماهیانه موجود.
    نیاز به ورود به سیستم و مجوز تغییر رکورد کارکرد (در سازمان مربوطه) دارد.
    """
    model = MonthlyWorkRecord
    form_class = MonthlyWorkRecordForm
    template_name = 'hr/monthlyworkrecord_form.html'
    context_object_name = 'monthlyworkrecord'
    success_message = "رکورد کارکرد ماهیانه با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_monthlyworkrecord' permission in the organization of the work record
        record = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, record.organization, 'hr.change_monthlyworkrecord')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['employee'] = self.object.employee
        kwargs['organization'] = self.object.organization
        kwargs['financial_period'] = self.object.financial_period
        return kwargs


    def get_success_url(self):
        employee_pk = self.object.employee.pk
        financial_period_pk = self.object.financial_period.pk
        return reverse_lazy('hr:monthlyworkrecord_list_by_employee_period', kwargs={'employee_pk': employee_pk, 'financial_period_pk': financial_period_pk})


class MonthlyWorkRecordDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """
    حذف رکورد کارکرد ماهیانه.
    نیاز به ورود به سیستم و مجوز حذف رکورد کارکرد (در سازمان مربوطه) دارد.
    """
    model = MonthlyWorkRecord
    template_name = 'hr/monthlyworkrecord_confirm_delete.html'
    context_object_name = 'monthlyworkrecord'
    success_message = "رکورد کارکرد ماهیانه با موفقیت حذف شد."

    def test_func(self):
        # Check if the user has the 'delete_monthlyworkrecord' permission in the organization of the work record
        record = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, record.organization, 'hr.delete_monthlyworkrecord')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Note: Detail Views can be added for any of the models if needed.
