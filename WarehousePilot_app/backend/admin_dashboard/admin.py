from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auth_app.models import users

@admin.register(users)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'department', 'is_active', 'is_staff')
    list_filter = ('role', 'department', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'dob')}),
        ('Department info', {'fields': ('department', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'department', 'dob', 'first_name', 'last_name'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('is_superuser', 'user_permissions', 'groups')
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete users
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Users can only edit their own profile unless they're admin/superuser
        if obj is None:
            return True
        return request.user.is_superuser or request.user.role == 'admin' or request.user == obj
