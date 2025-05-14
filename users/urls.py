from django.urls import path
# Import views from the current app
from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,

    OrganizationRoleListView,
    OrganizationRoleCreateView,
    OrganizationRoleUpdateView,
    OrganizationRoleDeleteView,

    UserOrganizationRoleListView,
    UserOrganizationRoleCreateView,
    UserOrganizationRoleUpdateView,
    UserOrganizationRoleDeleteView,
    # DetailViews if you create them
    # OrganizationRoleDetailView,
    # UserOrganizationRoleDetailView,
)

app_name = 'users' # Namespace for this app's URLs

urlpatterns = [
    # --- Authentication URLs (Existing) ---
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'), # Optional: If registration is enabled


    # --- URLs for OrganizationRole (Management of Organization Roles) ---
    # List Organization Roles (general list)
    path('roles/', OrganizationRoleListView.as_view(), name='organizationrole_list'),
    # List Organization Roles filtered by Organization
    # Example: /users/organization/5/roles/
    path('organization/<int:organization_pk>/roles/', OrganizationRoleListView.as_view(), name='organizationrole_list_by_org'),
    # Create Organization Role
    path('roles/create/', OrganizationRoleCreateView.as_view(), name='organizationrole_create'),
    # Create Organization Role for a specific Organization (initial organization field)
    path('organization/<int:organization_pk>/roles/create/', OrganizationRoleCreateView.as_view(), name='organizationrole_create_in_org'),
    # Update a specific Organization Role
    path('roles/<int:pk>/update/', OrganizationRoleUpdateView.as_view(), name='organizationrole_update'),
    # Delete a specific Organization Role
    path('roles/<int:pk>/delete/', OrganizationRoleDeleteView.as_view(), name='organizationrole_delete'),
    # Detail view for OrganizationRole (Optional)
    # path('roles/<int:pk>/', OrganizationRoleDetailView.as_view(), name='organizationrole_detail'),


    # --- URLs for UserOrganizationRole (Assignment of Organization Roles to Users) ---
    # List User Organization Roles (general list)
    path('user-roles/', UserOrganizationRoleListView.as_view(), name='userorganizationrole_list'),
    # List User Organization Roles filtered by Organization
    # Example: /users/organization/5/user-roles/
    path('organization/<int:organization_pk>/user-roles/', UserOrganizationRoleListView.as_view(), name='userorganizationrole_list_by_org'),
    # List User Organization Roles filtered by User
    # Example: /users/user/10/user-roles/
    path('user/<int:user_pk>/user-roles/', UserOrganizationRoleListView.as_view(), name='userorganizationrole_list_by_user'),
    # Create User Organization Role
    path('user-roles/create/', UserOrganizationRoleCreateView.as_view(), name='userorganizationrole_create'),
    # Create User Organization Role for a specific Organization (initial organization field)
    path('organization/<int:organization_pk>/user-roles/create/', UserOrganizationRoleCreateView.as_view(), name='userorganizationrole_create_in_org'),
    # Create User Organization Role for a specific User (initial user field)
    path('user/<int:user_pk>/user-roles/create/', UserOrganizationRoleCreateView.as_view(), name='userorganizationrole_create_for_user'),
    # Create User Organization Role for a specific User and Organization (initial fields)
    path('user/<int:user_pk>/organization/<int:organization_pk>/user-roles/create/', UserOrganizationRoleCreateView.as_view(), name='userorganizationrole_create_for_user_org'),
    # Update a specific User Organization Role
    path('user-roles/<int:pk>/update/', UserOrganizationRoleUpdateView.as_view(), name='userorganizationrole_update'),
    # Delete a specific User Organization Role
    path('user-roles/<int:pk>/delete/', UserOrganizationRoleDeleteView.as_view(), name='userorganizationrole_delete'),
    # Detail view for UserOrganizationRole (Optional)
    # path('user-roles/<int:pk>/', UserOrganizationRoleDetailView.as_view(), name='userorganizationrole_detail'),
]
