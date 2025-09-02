from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin interface for Supplier model."""
    
    list_display = ('code', 'name', 'trade_name', 'supplier_type', 'city', 'state', 'phone', 'email', 'is_active')
    list_filter = ('supplier_type', 'state', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'trade_name', 'cnpj_cpf', 'email', 'phone', 'city')
    ordering = ('code',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'trade_name', 'supplier_type')
        }),
        ('Documents', {
            'fields': ('cnpj_cpf', 'state_registration', 'municipal_registration'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'mobile', 'website')
        }),
        ('Address', {
            'fields': ('address', 'address_number', 'address_complement', 'neighborhood', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': ('contact_person', 'contact_email', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': ('payment_terms', 'credit_limit'),
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
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related()
