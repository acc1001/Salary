from django.urls import path
# Import Class-Based Views from the current app
from .views import (
    DepartmentListView,
    DepartmentCreateView,
    DepartmentUpdateView,
    DepartmentDeleteView,

    JobTitleListView,
    JobTitleCreateView,
    JobTitleUpdateView,
    JobTitleDeleteView,

    EmploymentHistoryListView,
    EmploymentHistoryCreateView,
    EmploymentHistoryUpdateView,
    EmploymentHistoryDeleteView,

    MonthlyWorkRecordListView,
    MonthlyWorkRecordCreateView,
    MonthlyWorkRecordUpdateView,
    MonthlyWorkRecordDeleteView,

    # Import DetailViews if you create them later
    # DepartmentDetailView,
    # JobTitleDetailView,
    # EmploymentHistoryDetailView,
    # MonthlyWorkRecordDetailView,
)

app_name = 'hr' # Namespace for this app's URLs

urlpatterns = [
    # --- URLs for Department ---
    # List Departments (can be filtered by organization)
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('organization/<int:organization_pk>/departments/', DepartmentListView.as_view(), name='department_list_by_org'),
    # Create Department
    path('departments/create/', DepartmentCreateView.as_view(), name='department_create'),
    path('organization/<int:organization_pk>/departments/create/', DepartmentCreateView.as_view(), name='department_create_in_org'),
    # Update Department
    path('departments/<int:pk>/update/', DepartmentUpdateView.as_view(), name='department_update'),
    # Delete Department
    path('departments/<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department_delete'),
    # Detail Department (Optional)
    # path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department_detail'),

    # --- URLs for JobTitle ---
    # List Job Titles (can be filtered by organization)
    path('job-titles/', JobTitleListView.as_view(), name='jobtitle_list'),
    path('organization/<int:organization_pk>/job-titles/', JobTitleListView.as_view(), name='jobtitle_list_by_org'),
    # Create Job Title
    path('job-titles/create/', JobTitleCreateView.as_view(), name='jobtitle_create'),
    path('organization/<int:organization_pk>/job-titles/create/', JobTitleCreateView.as_view(), name='jobtitle_create_in_org'),
    # Update Job Title
    path('job-titles/<int:pk>/update/', JobTitleUpdateView.as_view(), name='jobtitle_update'),
    # Delete Job Title
    path('job-titles/<int:pk>/delete/', JobTitleDeleteView.as_view(), name='jobtitle_delete'),
    # Detail Job Title (Optional)
    # path('job-titles/<int:pk>/', JobTitleDetailView.as_view(), name='jobtitle_detail'),

    # --- URLs for EmploymentHistory ---
    # List Employment History (can be filtered by employee or organization)
    path('employment-history/', EmploymentHistoryListView.as_view(), name='employmenthistory_list'),
    path('employee/<int:employee_pk>/employment-history/', EmploymentHistoryListView.as_view(), name='employmenthistory_list_by_employee'),
    path('organization/<int:organization_pk>/employment-history/', EmploymentHistoryListView.as_view(), name='employmenthistory_list_by_org'),
    # Create Employment History
    path('employment-history/create/', EmploymentHistoryCreateView.as_view(), name='employmenthistory_create'),
    path('employee/<int:employee_pk>/employment-history/create/', EmploymentHistoryCreateView.as_view(), name='employmenthistory_create_for_employee'),
    # Update Employment History
    path('employment-history/<int:pk>/update/', EmploymentHistoryUpdateView.as_view(), name='employmenthistory_update'),
    # Delete Employment History
    path('employment-history/<int:pk>/delete/', EmploymentHistoryDeleteView.as_view(), name='employmenthistory_delete'),
    # Detail Employment History (Optional)
    # path('employment-history/<int:pk>/', EmploymentHistoryDetailView.as_view(), name='employmenthistory_detail'),

    # --- URLs for MonthlyWorkRecord ---
    # List Monthly Work Records (can be filtered by employee, organization, or financial period)
    path('work-records/', MonthlyWorkRecordListView.as_view(), name='monthlyworkrecord_list'),
    path('employee/<int:employee_pk>/work-records/', MonthlyWorkRecordListView.as_view(), name='monthlyworkrecord_list_by_employee'),
    path('organization/<int:organization_pk>/work-records/', MonthlyWorkRecordListView.as_view(), name='monthlyworkrecord_list_by_org'),
    path('period/<int:financial_period_pk>/work-records/', MonthlyWorkRecordListView.as_view(), name='monthlyworkrecord_list_by_period'),
    path('employee/<int:employee_pk>/period/<int:financial_period_pk>/work-records/', MonthlyWorkRecordListView.as_view(), name='monthlyworkrecord_list_by_employee_period'),
    # Create Monthly Work Record
    path('work-records/create/', MonthlyWorkRecordCreateView.as_view(), name='monthlyworkrecord_create'),
    path('employee/<int:employee_pk>/period/<int:financial_period_pk>/work-records/create/', MonthlyWorkRecordCreateView.as_view(), name='monthlyworkrecord_create_for_employee_period'),
    # Update Monthly Work Record
    path('work-records/<int:pk>/update/', MonthlyWorkRecordUpdateView.as_view(), name='monthlyworkrecord_update'),
    # Delete Monthly Work Record
    path('work-records/<int:pk>/delete/', MonthlyWorkRecordDeleteView.as_view(), name='monthlyworkrecord_delete'),
    # Detail Monthly Work Record (Optional)
    # path('work-records/<int:pk>/', MonthlyWorkRecordDetailView.as_view(), name='monthlyworkrecord_detail'),
]
