from django.urls import path
# Import Class-Based Views from the current app
from .views import (
    EmployeeLoanListView,
    EmployeeLoanCreateView,
    EmployeeLoanUpdateView,
    EmployeeLoanDeleteView,
    # Import DetailView if you create it later
    # EmployeeLoanDetailView,
)

app_name = 'loans' # Namespace for this app's URLs

urlpatterns = [
    # --- URLs for EmployeeLoan ---
    # List Employee Loans (general list)
    path('', EmployeeLoanListView.as_view(), name='employeeloan_list'),
    # List Employee Loans filtered by Employee
    # Example: /loans/employee/10/
    path('employee/<int:employee_pk>/', EmployeeLoanListView.as_view(), name='employeeloan_list_by_employee'),
    # List Employee Loans filtered by Organization
    # Example: /loans/organization/5/
    path('organization/<int:organization_pk>/', EmployeeLoanListView.as_view(), name='employeeloan_list_by_org'),

    # Create Employee Loan
    # Can be created from a general page or filtered page
    path('create/', EmployeeLoanCreateView.as_view(), name='employeeloan_create'),
    # Create Employee Loan for a specific Employee (initial employee field)
    path('employee/<int:employee_pk>/create/', EmployeeLoanCreateView.as_view(), name='employeeloan_create_for_employee'),
    # Create Employee Loan for a specific Organization (initial organization field)
    path('organization/<int:organization_pk>/create/', EmployeeLoanCreateView.as_view(), name='employeeloan_create_for_org'),
    # Create Employee Loan for a specific Employee and Organization (initial fields)
    path('employee/<int:employee_pk>/organization/<int:organization_pk>/create/', EmployeeLoanCreateView.as_view(), name='employeeloan_create_for_employee_org'),


    # Update a specific Employee Loan
    # Example: /loans/1/update/
    path('<int:pk>/update/', EmployeeLoanUpdateView.as_view(), name='employeeloan_update'),

    # Delete a specific Employee Loan
    # Example: /loans/1/delete/
    path('<int:pk>/delete/', EmployeeLoanDeleteView.as_view(), name='employeeloan_delete'),

    # Detail view for EmployeeLoan (Optional)
    # path('<int:pk>/', EmployeeLoanDetailView.as_view(), name='employeeloan_detail'),
]
