from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Import UserAdmin
from .models import CustomUser, OrganizationRole, UserOrganizationRole
from .forms import CustomUserCreationForm, CustomUserChangeForm # Import custom forms

# Register your models here.

# Custom Admin for CustomUser
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for CustomUser model using custom forms.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active'] # Customize list display
    # Customize fieldsets for display and add forms
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'email',)}), # Add custom fields to display form
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'email',)}), # Add custom fields to add form
    )

admin.site.register(CustomUser, CustomUserAdmin)


# Admin for OrganizationRole
class OrganizationRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for OrganizationRole model.
    """
    list_display = ['organization', 'name', 'created_at']
    list_filter = ['organization'] # Filter by organization
    search_fields = ['name', 'organization__name'] # Search by role name or organization name
    # You can add a filter for permissions if needed, but permissions are many-to-many

admin.site.register(OrganizationRole, OrganizationRoleAdmin)


# Admin for UserOrganizationRole
class UserOrganizationRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for UserOrganizationRole model.
    """
    list_display = ['user', 'organization', 'role', 'created_at']
    list_filter = ['organization', 'role'] # Filter by organization and role
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'organization__name', 'role__name'] # Search by user or organization/role names
    raw_id_fields = ['user', 'organization', 'role'] # Use raw_id_fields for ForeignKey/ManyToManyField if many objects exist

admin.site.register(UserOrganizationRole, UserOrganizationRoleAdmin)

