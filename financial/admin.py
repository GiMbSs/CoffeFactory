from django.contrib import admin
from .models import AccountsReceivable, AccountsReceivablePayment, AccountsPayable, AccountsPayablePayment, Payroll


class AccountsReceivablePaymentInline(admin.TabularInline):
    """Inline admin for AccountsReceivablePayment."""
    model = AccountsReceivablePayment
    extra = 0
    fields = ('amount', 'payment_date', 'payment_method', 'reference_number')
    readonly_fields = ('created_at',)


class AccountsPayablePaymentInline(admin.TabularInline):
    """Inline admin for AccountsPayablePayment."""
    model = AccountsPayablePayment
    extra = 0
    fields = ('amount', 'payment_date', 'payment_method', 'reference_number')
    readonly_fields = ('created_at',)


@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(admin.ModelAdmin):
    """Admin interface for AccountsReceivable model."""
    
    list_display = ('invoice_number', 'customer', 'original_amount', 'paid_amount', 'balance_display', 'status', 'due_date', 'is_overdue_display')
    list_filter = ('status', 'payment_method', 'due_date', 'issue_date')
    search_fields = ('invoice_number', 'customer__name', 'customer__code', 'description')
    ordering = ('due_date', '-issue_date')
    date_hierarchy = 'due_date'
    inlines = [AccountsReceivablePaymentInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'customer', 'sales_order', 'status')
        }),
        ('Financial Information', {
            'fields': ('original_amount', 'paid_amount', 'discount_amount', 'interest_amount', 'fine_amount')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'payment_date')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'bank_account', 'reference_number'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('description', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def balance_display(self, obj):
        """Display balance with currency."""
        return f"R$ {obj.balance:,.2f}"
    balance_display.short_description = 'Balance'
    
    def is_overdue_display(self, obj):
        """Display overdue status."""
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = 'Overdue'


@admin.register(AccountsReceivablePayment)
class AccountsReceivablePaymentAdmin(admin.ModelAdmin):
    """Admin interface for AccountsReceivablePayment model."""
    
    list_display = ('receivable', 'amount', 'payment_date', 'payment_method', 'reference_number')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('receivable__invoice_number', 'reference_number')
    ordering = ('-payment_date',)
    date_hierarchy = 'payment_date'
    
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AccountsPayable)
class AccountsPayableAdmin(admin.ModelAdmin):
    """Admin interface for AccountsPayable model."""
    
    list_display = ('invoice_number', 'supplier', 'expense_type', 'original_amount', 'paid_amount', 'balance_display', 'status', 'due_date', 'is_overdue_display')
    list_filter = ('status', 'expense_type', 'payment_method', 'due_date', 'invoice_date')
    search_fields = ('invoice_number', 'supplier__name', 'supplier__code', 'description')
    ordering = ('due_date', '-invoice_date')
    date_hierarchy = 'due_date'
    inlines = [AccountsPayablePaymentInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'supplier', 'expense_type', 'status')
        }),
        ('Financial Information', {
            'fields': ('original_amount', 'paid_amount', 'discount_amount', 'interest_amount', 'fine_amount')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'payment_date')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'bank_account', 'reference_number'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('description', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def balance_display(self, obj):
        """Display balance with currency."""
        return f"R$ {obj.balance:,.2f}"
    balance_display.short_description = 'Balance'
    
    def is_overdue_display(self, obj):
        """Display overdue status."""
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = 'Overdue'


@admin.register(AccountsPayablePayment)
class AccountsPayablePaymentAdmin(admin.ModelAdmin):
    """Admin interface for AccountsPayablePayment model."""
    
    list_display = ('payable', 'amount', 'payment_date', 'payment_method', 'reference_number')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('payable__invoice_number', 'reference_number')
    ordering = ('-payment_date',)
    date_hierarchy = 'payment_date'
    
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    """Admin interface for Payroll model."""
    
    list_display = ('payroll_number', 'employee', 'reference_month', 'status', 'gross_salary', 'net_salary', 'payment_date')
    list_filter = ('status', 'reference_month', 'employee__department')
    search_fields = ('payroll_number', 'employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    ordering = ('-reference_month', 'employee__user__first_name')
    date_hierarchy = 'reference_month'
    
    fieldsets = (
        ('Payroll Information', {
            'fields': ('payroll_number', 'employee', 'reference_month', 'status')
        }),
        ('Work Information', {
            'fields': ('days_worked', 'hours_worked', 'overtime_hours')
        }),
        ('Earnings', {
            'fields': ('base_salary', 'overtime_amount', 'bonus_amount', 'commission_amount', 'other_earnings', 'gross_salary'),
            'classes': ('collapse',)
        }),
        ('Deductions', {
            'fields': ('inss_amount', 'irrf_amount', 'health_insurance', 'dental_insurance', 'meal_voucher_discount', 'transport_voucher_discount', 'union_dues', 'other_deductions', 'total_deductions'),
            'classes': ('collapse',)
        }),
        ('Final Amounts', {
            'fields': ('net_salary',)
        }),
        ('Payment Information', {
            'fields': ('payment_date', 'payment_method', 'bank_account'),
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
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'gross_salary', 'total_deductions', 'net_salary')
    
    actions = ['calculate_payrolls', 'process_payrolls']
    
    def calculate_payrolls(self, request, queryset):
        """Calculate selected payrolls."""
        count = 0
        for payroll in queryset:
            payroll.calculate_net_salary()
            payroll.save()
            count += 1
        self.message_user(request, f'{count} payrolls calculated successfully.')
    calculate_payrolls.short_description = 'Calculate selected payrolls'
    
    def process_payrolls(self, request, queryset):
        """Process selected payrolls."""
        count = 0
        for payroll in queryset:
            payroll.process_payroll()
            count += 1
        self.message_user(request, f'{count} payrolls processed successfully.')
    process_payrolls.short_description = 'Process selected payrolls'
