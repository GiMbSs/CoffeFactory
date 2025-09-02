from django.contrib import admin
from .models import Customer, SalesOrder, SalesOrderItem


class SalesOrderItemInline(admin.TabularInline):
    """Inline admin for SalesOrderItem."""
    model = SalesOrderItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer model."""
    
    list_display = ('code', 'name', 'trade_name', 'customer_type', 'status', 'city', 'state', 'phone', 'email')
    list_filter = ('customer_type', 'status', 'state', 'created_at')
    search_fields = ('code', 'name', 'trade_name', 'cnpj_cpf', 'email', 'phone', 'city')
    ordering = ('code',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'trade_name', 'customer_type', 'status')
        }),
        ('Documents', {
            'fields': ('cnpj_cpf', 'state_registration'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'mobile')
        }),
        ('Address', {
            'fields': ('address', 'address_number', 'address_complement', 'neighborhood', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Sales Information', {
            'fields': ('sales_representative', 'credit_limit', 'payment_terms', 'discount_percentage'),
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


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    """Admin interface for SalesOrder model."""
    
    list_display = ('order_number', 'customer', 'status', 'priority', 'order_date', 'delivery_date', 'total_amount')
    list_filter = ('status', 'priority', 'order_date', 'delivery_date')
    search_fields = ('order_number', 'customer__name', 'customer__code', 'notes')
    ordering = ('-order_date',)
    date_hierarchy = 'order_date'
    inlines = [SalesOrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'priority')
        }),
        ('Dates', {
            'fields': ('order_date', 'delivery_date', 'actual_delivery_date')
        }),
        ('Sales Information', {
            'fields': ('sales_representative', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'order_date')


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for SalesOrderItem model."""
    
    list_display = ('sales_order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('sales_order__status', 'product__category')
    search_fields = ('sales_order__order_number', 'product__name', 'product__code')
    ordering = ('sales_order', 'product')
    
    readonly_fields = ('id', 'total_price', 'created_at', 'updated_at')
