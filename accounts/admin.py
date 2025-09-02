from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Employee


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_employee', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_employee', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Info', {
            'fields': ('phone', 'is_employee')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Info', {
            'fields': ('email', 'phone', 'is_employee')
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee model."""
    
    list_display = ('employee_id', 'get_full_name', 'department', 'position', 'employment_type', 'hire_date', 'is_active')
    list_filter = ('department', 'employment_type', 'is_active', 'hire_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email', 'position')
    ordering = ('employee_id',)
    date_hierarchy = 'hire_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Employee Information', {
            'fields': ('employee_id', 'department', 'position', 'employment_type', 'hire_date', 'salary')
        }),
        ('Contact Information', {
            'fields': ('address', 'emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        """Get employee full name."""
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
