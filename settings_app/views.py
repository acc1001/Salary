from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


# import مدل‌ها و فرم‌ها
from .models import FiscalYear, InsuranceCeiling, TaxLevel, FinancialPeriod
from .forms import FiscalYearForm, InsuranceCeilingForm, TaxLevelForm, FinancialPeriodForm

# Import Organization model and CustomUser model for permission checks
from organizations.models import Organization
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


# ویوهای مدیریت سال‌های مالی (FiscalYear)
class FiscalYearListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست تمامی سال‌های مالی.
    نیاز به ورود به سیستم و مجوز مشاهده سال‌های مالی دارد.
    """
    model = FiscalYear
    template_name = 'settings_app/fiscal_year_list.html'
    context_object_name = 'fiscal_years'
    # paginate_by = 10 # اضافه کردن صفحه بندی (اختیاری)

    def test_func(self):
        # Check if the user has the general 'view_fiscalyear' permission or is staff/superuser
        # For organization-specific view permission, filter the queryset instead.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('settings_app.view_fiscalyear')


    def get_queryset(self):
        # Filter fiscal years based on user's access to the organization
        if self.request.user.is_staff or self.request.user.is_superuser:
            return FiscalYear.objects.all()
        else:
            # Show only fiscal years in organizations the user has permission to view them in
            # This requires defining what "permission to view fiscal years in an organization" means.
            # Let's assume it means having 'settings_app.view_fiscalyear' permission in that organization.
            user_accessible_org_ids = [
                org.pk for org in Organization.objects.all() # Or a subset of organizations
                if has_org_permission(self.request.user, org, 'settings_app.view_fiscalyear')
            ]
            return FiscalYear.objects.filter(organization__pk__in=user_accessible_org_ids)


class FiscalYearCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد سال مالی جدید.
    نیاز به ورود به سیستم و مجوز افزودن سال مالی (در سازمان مربوطه) دارد.
    """
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'settings_app/fiscal_year_form.html'
    success_message = "سال مالی با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the general 'add_fiscalyear' permission or is staff/superuser
        # For organization-specific permission, check in form_valid based on selected organization.
        return self.request.user.is_staff or self.request.user.is_superuser or \
               self.request.user.has_perm('settings_app.add_fiscalyear')

    def form_valid(self, form):
        # Check organization-specific permission before saving based on the selected organization
        organization = form.cleaned_data.get('organization')
        if organization:
            if not has_org_permission(self.request.user, organization, 'settings_app.add_fiscalyear'):
                 messages.error(self.request, _("شما مجوز افزودن سال مالی در این سازمان را ندارید."))
                 return self.form_invalid(form) # Return invalid form with error message

        return super().form_valid(form)

    def get_success_url(self):
        # Try to redirect to the list filtered by the organization of the created object
        if self.object.organization:
             # Note: We don't have a fiscal_year_list_by_org URL pattern currently.
             # Redirecting to the general list for now, or you need to add that URL pattern.
             # return reverse_lazy('settings_app:fiscal_year_list_by_org', kwargs={'organization_pk': self.object.organization.pk})
             pass # Fallback to the general list defined in success_url


class FiscalYearUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش سال مالی موجود.
    نیاز به ورود به سیستم و مجوز تغییر سال مالی (در سازمان مربوطه) دارد.
    """
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'settings_app/fiscal_year_form.html'
    context_object_name = 'fiscal_year'
    success_message = "سال مالی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_fiscalyear' permission in the organization of the fiscal year
        fiscal_year = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.change_fiscalyear')

    def get_success_url(self):
        return reverse_lazy('settings_app:fiscal_year_list')


# ویوهای مدیریت سقف‌های بیمه (InsuranceCeiling)
# توجه: این ویوها به یک سال مالی خاص مرتبط هستند و fiscal_year_pk را از URL دریافت می‌کنند.

class InsuranceCeilingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست سقف‌های بیمه برای یک سال مالی خاص.
    نیاز به ورود به سیستم و مجوز مشاهده سقف‌های بیمه (در سازمان مربوطه) دارد.
    """
    model = InsuranceCeiling
    template_name = 'settings_app/insurance_ceiling_list.html'
    context_object_name = 'insurance_ceilings'

    def test_func(self):
        # Check if the user has the 'view_insuranceceiling' permission in the organization of the fiscal year
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.view_insuranceceiling')


    def get_queryset(self):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return InsuranceCeiling.objects.filter(fiscal_year=fiscal_year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fiscal_year'] = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return context


class InsuranceCeilingCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد سقف بیمه جدید برای یک سال مالی خاص.
    نیاز به ورود به سیستم و مجوز افزودن سقف بیمه (در سازمان مربوطه) دارد.
    """
    model = InsuranceCeiling
    form_class = InsuranceCeilingForm
    template_name = 'settings_app/insurance_ceiling_form.html'
    success_message = "سقف بیمه با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the 'add_insuranceceiling' permission in the organization of the fiscal year
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.add_insuranceceiling')


    def form_valid(self, form):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        form.instance.fiscal_year = fiscal_year
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('settings_app:insurance_ceiling_list', kwargs={'fiscal_year_pk': self.kwargs['fiscal_year_pk']})


class InsuranceCeilingUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش سقف بیمه موجود.
    نیاز به ورود به سیستم و مجوز تغییر سقف بیمه (در سازمان مربوطه) دارد.
    """
    model = InsuranceCeiling
    form_class = InsuranceCeilingForm
    template_name = 'settings_app/insurance_ceiling_form.html'
    context_object_name = 'insurance_ceiling'
    success_message = "سقف بیمه با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_insuranceceiling' permission in the organization of the fiscal year
        insurance_ceiling = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, insurance_ceiling.fiscal_year.organization, 'settings_app.change_insuranceceiling')


    def get_success_url(self):
        return reverse_lazy('settings_app:insurance_ceiling_list', kwargs={'fiscal_year_pk': self.object.fiscal_year.pk})


# ویوهای مدیریت سطوح مالیاتی (TaxLevel)
# توجه: این ویوها به یک سال مالی خاص مرتبط هستند و fiscal_year_pk را از URL دریافت می‌کنند.

class TaxLevelListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست سطوح مالیاتی برای یک سال مالی خاص.
    نیاز به ورود به سیستم و مجوز مشاهده سطوح مالیاتی (در سازمان مربوطه) دارد.
    """
    model = TaxLevel
    template_name = 'settings_app/tax_level_list.html'
    context_object_name = 'tax_levels'

    def test_func(self):
        # Check if the user has the 'view_taxlevel' permission in the organization of the fiscal year
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.view_taxlevel')


    def get_queryset(self):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return TaxLevel.objects.filter(fiscal_year=fiscal_year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fiscal_year'] = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return context


class TaxLevelCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد سطح مالیاتی جدید برای یک سال مالی خاص.
    نیاز به ورود به سیستم و مجوز افزودن سطح مالیاتی (در سازمان مربوطه) دارد.
    """
    model = TaxLevel
    form_class = TaxLevelForm
    template_name = 'settings_app/tax_level_form.html'
    success_message = "سطح مالیاتی با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the 'add_taxlevel' permission in the organization of the fiscal year
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.add_taxlevel')


    def form_valid(self, form):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        form.instance.fiscal_year = fiscal_year
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('settings_app:tax_level_list', kwargs={'fiscal_year_pk': self.kwargs['fiscal_year_pk']})


class TaxLevelUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش سطح مالیاتی موجود.
    نیاز به ورود به سیستم و مجوز تغییر سطح مالیاتی (در سازمان مربوطه) دارد.
    """
    model = TaxLevel
    form_class = TaxLevelForm
    template_name = 'settings_app/tax_level_form.html'
    context_object_name = 'tax_level'
    success_message = "سطح مالیاتی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_taxlevel' permission in the organization of the fiscal year
        tax_level = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, tax_level.fiscal_year.organization, 'settings_app.change_taxlevel')


    def get_success_url(self):
        return reverse_lazy('settings_app:tax_level_list', kwargs={'fiscal_year_pk': self.object.fiscal_year.pk})


# ویوهای مدیریت دوره‌های مالی (FinancialPeriod)
# توجه: این ویوها به یک سال مالی خاص مرتبط هستند و fiscal_year_pk را از URL دریافت می‌کنند.

class FinancialPeriodListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    نمایش لیست تمامی دوره‌های مالی برای یک سال مالی خاص.
    نیاز به ورود به سیستم و مجوز مشاهده دوره‌های مالی (در سازمان مربوطه) دارد.
    """
    model = FinancialPeriod
    template_name = 'settings_app/financial_period_list.html'
    context_object_name = 'financial_periods'

    def test_func(self):
        # Check if the user has the 'view_financialperiod' permission in the organization of the fiscal year
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.view_financialperiod')


    def get_queryset(self):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return FinancialPeriod.objects.filter(fiscal_year=fiscal_year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fiscal_year'] = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return context


class FinancialPeriodCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد دوره مالی جدید برای یک سال مالی خاص.
    نیاز به ورود به سیستم و مجوز افزودن دوره مالی (در سازمان مربوطه) دارد.
    """
    model = FinancialPeriod
    form_class = FinancialPeriodForm
    template_name = 'settings_app/financial_period_form.html'
    success_message = "دوره مالی با موفقیت ایجاد شد."

    def test_func(self):
        # Check if the user has the 'add_financialperiod' permission in the organization of the fiscal year
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, fiscal_year.organization, 'settings_app.add_financialperiod')


    def form_valid(self, form):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_pk'])
        form.instance.fiscal_year = fiscal_year
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('settings_app:financial_period_list', kwargs={'fiscal_year_pk': self.kwargs['fiscal_year_pk']})


class FinancialPeriodUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش دوره مالی موجود.
    نیاز به ورود به سیستم و مجوز تغییر دوره مالی (در سازمان مربوطه) دارد.
    """
    model = FinancialPeriod
    form_class = FinancialPeriodForm
    template_name = 'settings_app/financial_period_form.html'
    context_object_name = 'financial_period'
    success_message = "دوره مالی با موفقیت به‌روزرسانی شد."

    def test_func(self):
        # Check if the user has the 'change_financialperiod' permission in the organization of the fiscal year
        financial_period = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or \
               has_org_permission(self.request.user, financial_period.fiscal_year.organization, 'settings_app.change_financialperiod')


    def get_success_url(self):
        return reverse_lazy('settings_app:financial_period_list', kwargs={'fiscal_year_pk': self.object.fiscal_year.pk})

# Note: Add DeleteViews and corresponding permission checks when implemented.
