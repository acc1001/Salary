from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test # Import user_passes_test
from django.contrib import messages
from employees.models import Employee
from django.utils.translation import gettext_lazy as _



# import مدل‌های باقی‌مانده در اپ employees
from .models import Employee, BankAccount

# اگر ویوهای خاصی در employees به مدل‌های سازمان نیاز دارند، آنها را از organizations.models وارد کنید
from organizations.models import Organization, EmployeeOrganization

# Import CustomUser model to use has_organization_permission method
from users.models import CustomUser # Assuming CustomUser is in users.models


# Helper function to check organization-specific permission
def has_org_permission(user, organization, perm_name):
    """
    Checks if the user has the specified permission in the given organization.
    Assumes user is an instance of CustomUser with the has_organization_permission method.
    """
    if not isinstance(user, CustomUser):
        # Handle cases where user is not CustomUser (e.g., AnonymousUser)
        return False
    return user.has_organization_permission(organization, perm_name)

# Predicate for user_passes_test decorator
def user_can_view_employees_in_org(user):
    """
    Checks if the user can view employees in any organization they are related to.
    This is a simplified check; you might need a more specific one based on the view's context.
    For list views filtered by organization, you'd need the organization object.
    """
    # This predicate is too general for organization-specific lists.
    # For organization-specific views, it's better to get the organization in the view
    # and then use has_org_permission.
    # For a general list, you might check if the user has permission in ANY organization they belong to.
    # Example (more complex): Check if the user has the permission in at least one organization they are a member of.
    # user_orgs = user.user_organization_roles.values_list('organization', flat=True)
    # return any(user.has_organization_permission(org, 'employees.view_employee') for org in Organization.objects.filter(pk__in=user_orgs))
    # For now, a simple check for staff/superuser or a general permission might suffice for the *general* list.
    return user.is_staff or user.is_superuser # Simplified check for general list


def user_can_manage_employees_in_org(user, organization_pk):
    """
    Checks if the user can manage (create/update/delete) employees in a specific organization.
    """
    try:
        organization = Organization.objects.get(pk=organization_pk)
        # Check if the user has the 'add_employee' or 'change_employee' permission in this organization
        return has_org_permission(user, organization, 'employees.add_employee') or \
               has_org_permission(user, organization, 'employees.change_employee')
    except Organization.DoesNotExist:
        return False # Organization not found


# ویوهای فانکشنال مدیریت کارمندان (بر اساس کدهای اولیه شما)

# نمایش فهرست کارمندان
# This view currently shows ALL employees.
# For organization-specific filtering, you'd need organization_pk in the URL
# and filter the queryset, and check permission for that specific organization.
# For a general list, you might check if the user has permission to view employees
# in at least one organization they belong to, or if they are staff/superuser.
@login_required # اعمال دسترسی ورود
# @user_passes_test(user_can_view_employees_in_org) # Apply general permission check (adjust predicate as needed)
def employee_list(request):
    """
    نمایش لیست تمامی کارمندان (یا فیلتر شده بر اساس سازمان).
    """
    organization_pk = request.GET.get('organization_pk') # Example: filter by query parameter

    if organization_pk:
        organization = get_object_or_404(Organization, pk=organization_pk)
        # Check organization-specific permission to view employees in this organization
        if not has_org_permission(request.user, organization, 'employees.view_employee'):
             messages.error(request, _("شما مجوز مشاهده کارکنان این سازمان را ندارید."))
             return redirect('home') # Redirect to home or a permission denied page

        employees = Employee.objects.filter(employee_organizations__organization=organization).distinct()
        context = {'employees': employees, 'organization': organization}
    else:
        # General list - requires broader permission or shows only employees in user's orgs
        # For simplicity, let's show all employees for staff/superuser, or none otherwise (needs refinement)
        if request.user.is_staff or request.user.is_superuser:
             employees = Employee.objects.all()
             context = {'employees': employees}
        else:
             # Show only employees in organizations the user has permission to view
             # This requires more complex filtering based on user's roles/permissions across organizations
             # For now, let's redirect or show empty if not staff/superuser and no org filter
             messages.warning(request, _("لطفاً سازمان مورد نظر را برای مشاهده کارکنان انتخاب کنید."))
             return render(request, 'employees/employee_list.html', {'employees': []}) # Show empty list or redirect


    return render(request, 'employees/employee_list.html', context)


# ایجاد کارمند جدید
# Requires organization_pk in URL or form to check organization-specific permission
@login_required # اعمال دسترسی ورود
def employee_create(request):
    """
    ایجاد کارمند جدید.
    """
    from .forms import EmployeeForm # import داخلی

    # Get organization_pk from URL or form data to check permission
    organization_pk = request.POST.get('organization') or request.GET.get('organization_pk')

    if organization_pk:
        organization = get_object_or_404(Organization, pk=organization_pk)
        # Check organization-specific permission to add employees in this organization
        if not has_org_permission(request.user, organization, 'employees.add_employee'):
             messages.error(request, _("شما مجوز افزودن کارمند در این سازمان را ندارید."))
             return redirect('home') # Redirect to home or a permission denied page

        if request.method == 'POST':
            form = EmployeeForm(request.POST, request.FILES) # اضافه کردن request.FILES برای آپلود عکس
            if form.is_valid():
                employee_instance = form.save(commit=False)
                if request.user.is_authenticated: # Should be true due to @login_required
                    employee_instance.user_account = request.user # Assign current user account
                    employee_instance.save()

                    # Assuming EmployeeOrganization is used to link employee to organization
                    # You need to create an EmployeeOrganization instance here as well
                    # This might require additional fields in the form or initial data
                    # For simplicity, let's assume organization is selected in the form
                    # or passed via initial data.
                    # Example: Create EmployeeOrganization entry
                    # EmployeeOrganization.objects.create(
                    #     employee=employee_instance,
                    #     organization=organization, # Use the organization obtained from pk
                    #     start_date=employee_instance.hire_date # Or another relevant date
                    # )


                    messages.success(request, "کارمند با موفقیت ایجاد شد.")
                    # Redirect to employee detail or list, potentially filtered by organization
                    return redirect('employees:employee_detail', pk=employee_instance.pk)
                else:
                     messages.error(request, "خطا در احراز هویت کاربر.")
                     return redirect('users:login')

        else: # GET request
            # Pass initial organization to the form if available
            initial_data = {}
            if organization_pk:
                 initial_data['organization'] = organization # Pass the organization object
            form = EmployeeForm(initial=initial_data)

        context = {'form': form, 'organization': organization} # Pass organization to context
        return render(request, 'employees/employee_form.html', context)
    else:
        # Handle case where organization is not specified (cannot check org-specific permission)
        messages.warning(request, _("لطفاً سازمان مورد نظر را برای افزودن کارمند انتخاب کنید."))
        # Redirect to a page to select organization or show a message
        return redirect('organizations:organization_list') # Example: Redirect to organization list


# نمایش جزئیات کارمند
# Requires permission to view employees in the organization the employee belongs to.
# This is complex as an employee can belong to multiple organizations.
# For simplicity, let's check if the user has permission in *any* organization the employee belongs to.
@login_required # اعمال دسترسی ورود
def employee_detail(request, pk):
    """
    نمایش جزئیات یک کارمند خاص.
    """
    employee = get_object_or_404(Employee, pk=pk)

    # Check if the user has permission to view this employee in any of their organizations
    user_can_view = False
    for emp_org in employee.employee_organizations.all():
         if has_org_permission(request.user, emp_org.organization, 'employees.view_employee'):
             user_can_view = True
             break # Found at least one organization where the user can view employees

    if not user_can_view and not request.user.is_superuser and not request.user.is_staff:
         messages.error(request, _("شما مجوز مشاهده جزئیات این کارمند را ندارید."))
         return redirect('home') # Redirect to home or a permission denied page


    bank_accounts = employee.bank_accounts.all()
    return render(request, 'employees/employee_detail.html', {'employee': employee, 'bank_accounts': bank_accounts})


# ویرایش کارمند
# Requires permission to change employees in the organization the employee belongs to.
# Similar to detail view, an employee can be in multiple orgs.
# Let's require permission in *any* organization the employee belongs to for simplicity.
@login_required # اعمال دسترسی ورود
def employee_update(request, pk):
    """
    ویرایش اطلاعات کارمند موجود.
    """
    employee = get_object_or_404(Employee, pk=pk)
    from .forms import EmployeeForm # import داخلی

    # Check if the user has permission to change this employee in any of their organizations
    user_can_change = False
    for emp_org in employee.employee_organizations.all():
         if has_org_permission(request.user, emp_org.organization, 'employees.change_employee'):
             user_can_change = True
             break # Found at least one organization where the user can change employees

    if not user_can_change and not request.user.is_superuser and not request.user.is_staff:
         messages.error(request, _("شما مجوز ویرایش این کارمند را ندارید."))
         return redirect('home') # Redirect to home or a permission denied page


    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات کارمند با موفقیت به‌روزرسانی شد.")
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/employee_form.html', {'form': form, 'employee': employee})


# ویوهای مدیریت حساب بانکی (BankAccount) - مرتبط با کارمند

# ایجاد حساب بانکی جدید برای یک کارمند خاص
# Requires permission to add bank accounts in the organization the employee belongs to.
# Let's require permission in *any* organization the employee belongs to for simplicity.
@login_required # اعمال دسترسی ورود
def bank_account_create(request, employee_id):
    """
    ایجاد حساب بانکی جدید برای کارمند مشخص.
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    from .forms import BankAccountForm # import داخلی

    # Check if the user has permission to add bank accounts for this employee
    user_can_add_bank_account = False
    for emp_org in employee.employee_organizations.all():
         if has_org_permission(request.user, emp_org.organization, 'employees.add_bankaccount'):
             user_can_add_bank_account = True
             break # Found at least one organization where the user can add bank accounts

    if not user_can_add_bank_account and not request.user.is_superuser and not request.user.is_staff:
         messages.error(request, _("شما مجوز افزودن حساب بانکی برای این کارمند را ندارید."))
         return redirect('employees:employee_detail', pk=employee.pk) # Redirect back to employee detail

    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            form.instance.employee = employee
            form.save()
            messages.success(request, "حساب بانکی با موفقیت اضافه شد.")
            return redirect('employees:employee_detail', pk=employee.pk)
    else: # GET request
        form = BankAccountForm()

    return render(request, 'employees/bank_account_form.html', {'form': form, 'employee': employee})

# Note: Add permission checks to BankAccount update/delete views as well when implemented.
