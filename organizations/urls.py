from django.urls import path
# import ویوهای کلاس بیس از همین اپ
from .views import (
    OrganizationListView,
    OrganizationCreateView,
    OrganizationUpdateView,
    OrganizationDeleteView, # اضافه شده

    EmployeeOrganizationListView,
    EmployeeOrganizationCreateView,
    EmployeeOrganizationUpdateView,
    EmployeeOrganizationDeleteView, # اضافه شده
)

app_name = 'organizations' # نام اپ برای جلوگیری از تداخل نام‌ها

urlpatterns = [
    # مسیرهای مدیریت سازمان‌ها (Organization)
    path('', OrganizationListView.as_view(), name='organization_list'), # مسیر ریشه اپ برای لیست سازمان‌ها
    path('create/', OrganizationCreateView.as_view(), name='organization_create'),
    path('<int:pk>/update/', OrganizationUpdateView.as_view(), name='organization_update'),
    path('<int:pk>/delete/', OrganizationDeleteView.as_view(), name='organization_delete'),
    # path('<int:pk>/', OrganizationDetailView.as_view(), name='organization_detail'), # در صورت اضافه کردن ویو جزئیات

    # مسیرهای مدیریت عضویت کارمند در سازمان (EmployeeOrganization)
    # مسیر لیست عضویت‌ها (می‌تواند فیلتر بر اساس سازمان یا کارمند داشته باشد)
    path('memberships/', EmployeeOrganizationListView.as_view(), name='employeeorganization_list'),
    # مسیر ایجاد عضویت جدید
    path('memberships/create/', EmployeeOrganizationCreateView.as_view(), name='employeeorganization_create'),
    # مسیر ویرایش عضویت
    path('memberships/<int:pk>/update/', EmployeeOrganizationUpdateView.as_view(), name='employeeorganization_update'),
    # مسیر حذف عضویت
    path('memberships/<int:pk>/delete/', EmployeeOrganizationDeleteView.as_view(), name='employeeorganization_delete'),
    # path('memberships/<int:pk>/', EmployeeOrganizationDetailView.as_view(), name='employeeorganization_detail'), # در صورت اضافه کردن ویو جزئیات

    # مثال‌هایی برای فیلتر کردن لیست عضویت‌ها بر اساس سازمان یا کارمند (اگر در ویوها پیاده‌سازی شود)
    # path('<int:organization_pk>/memberships/', EmployeeOrganizationListView.as_view(), name='employeeorganization_list_by_org'),
    # path('employees/<int:employee_pk>/memberships/', EmployeeOrganizationListView.as_view(), name='employeeorganization_list_by_employee'),
]
