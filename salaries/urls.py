from django.urls import path
# Import Class-Based Views from the current app
from .views import (
    SalaryItemTypeList,
    SalaryItemTypeCreate,
    SalaryItemTypeUpdate,
    SalaryItemTypeDelete,

    EmployeeSalaryItemListByEmployee,
    EmployeeSalaryItemCreate,
    EmployeeSalaryItemUpdate,
    EmployeeSalaryItemDelete,
    # Import DetailViews if you create them later
    # SalaryItemTypeDetail,
    # EmployeeSalaryItemDetail,
)

app_name = 'salaries' # Namespace for this app's URLs

urlpatterns = [
    # --- URLs for SalaryItemType (Management of Salary Item Types) ---
    # List Salary Item Types - Filtered by Organization and Financial Period
    # Example: /salaries/organization/1/period/5/item-types/
    path(
        'organization/<int:organization_pk>/period/<int:financial_period_pk>/item-types/',
        SalaryItemTypeList.as_view(),
        name='salaryitemtype_list'
    ),
    # Create Salary Item Type for a specific Organization and Financial Period
    # Example: /salaries/organization/1/period/5/item-types/create/
    path(
        'organization/<int:organization_pk>/period/<int:financial_period_pk>/item-types/create/',
        SalaryItemTypeCreate.as_view(),
        name='salaryitemtype_create'
    ),
    # Update a specific Salary Item Type
    # Example: /salaries/item-types/1/update/
    path(
        'item-types/<int:pk>/update/',
        SalaryItemTypeUpdate.as_view(),
        name='salaryitemtype_update'
    ),
    # Delete a specific Salary Item Type
    # Example: /salaries/item-types/1/delete/
    path(
        'item-types/<int:pk>/delete/',
        SalaryItemTypeDelete.as_view(),
        name='salaryitemtype_delete'
    ),
    # Detail view for SalaryItemType (Optional)
    # path('item-types/<int:pk>/', SalaryItemTypeDetail.as_view(), name='salaryitemtype_detail'),


    # --- URLs for EmployeeSalaryItem (Management of Employee Salary Items) ---
    # List Employee Salary Items for a specific Employee and Financial Period
    # Example: /salaries/employee/10/period/5/items/
    path(
        'employee/<int:employee_pk>/period/<int:financial_period_pk>/items/',
        EmployeeSalaryItemListByEmployee.as_view(),
        name='employeesalaryitem_list_by_employee'
    ),
    # Create Employee Salary Item for a specific Employee and Financial Period
    # Example: /salaries/employee/10/period/5/items/create/
    path(
        'employee/<int:employee_pk>/period/<int:financial_period_pk>/items/create/',
        EmployeeSalaryItemCreate.as_view(),
        name='employeesalaryitem_create'
    ),
    # Update a specific Employee Salary Item
    # Example: /salaries/items/25/update/
    path(
        'items/<int:pk>/update/',
        EmployeeSalaryItemUpdate.as_view(),
        name='employeesalaryitem_update'
    ),
    # Delete a specific Employee Salary Item
    # Example: /salaries/items/25/delete/
    path(
        'items/<int:pk>/delete/',
        EmployeeSalaryItemDelete.as_view(),
        name='employeesalaryitem_delete'
    ),
    # Detail view for EmployeeSalaryItem (Optional)
    # path('items/<int:pk>/', EmployeeSalaryItemDetail.as_view(), name='employeesalaryitem_detail'),

    # Note: You might need additional list views for EmployeeSalaryItem,
    # e.g., listing all items for a period across all employees,
    # or listing all items for an employee across all periods.
    # Example:
    # path('period/<int:financial_period_pk>/items/', EmployeeSalaryItemListByPeriod.as_view(), name='employeesalaryitem_list_by_period'),
    # path('employee/<int:employee_pk>/items/', EmployeeSalaryItemListByEmployeeAllPeriods.as_view(), name='employeesalaryitem_list_by_employee_all_periods'),
]
