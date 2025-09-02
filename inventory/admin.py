from django.contrib import admin
from .models import Category, UnitOfMeasure, Material, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    
    list_display = ('name', 'category_type', 'parent', 'is_active')
    list_filter = ('category_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('category_type', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category_type', 'parent')
        }),
        ('System Information', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    """Admin interface for UnitOfMeasure model."""
    
    list_display = ('name', 'abbreviation', 'description_short', 'materials_count', 'products_count', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'abbreviation', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'abbreviation', 'description')
        }),
        ('System Information', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def description_short(self, obj):
        """Short description for list display."""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
    def materials_count(self, obj):
        """Count of materials using this unit."""
        return obj.materials.filter(is_active=True).count()
    materials_count.short_description = 'Materials'
    
    def products_count(self, obj):
        """Count of products using this unit."""
        return obj.products.filter(is_active=True).count()
    products_count.short_description = 'Products'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """Admin interface for Material model."""
    
    list_display = ('code', 'name', 'category', 'unit_of_measure', 'cost_per_unit', 'current_stock_display', 'status')
    list_filter = ('category', 'unit_of_measure', 'status', 'supplier', 'created_at')
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'category', 'unit_of_measure')
        }),
        ('Financial Information', {
            'fields': ('cost_per_unit',)
        }),
        ('Stock Information', {
            'fields': ('minimum_stock', 'maximum_stock'),
            'classes': ('collapse',)
        }),
        ('Supplier Information', {
            'fields': ('supplier',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('status', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def current_stock_display(self, obj):
        """Display current stock with unit."""
        return f"{obj.current_stock} {obj.unit_of_measure.abbreviation}"
    current_stock_display.short_description = 'Current Stock'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    
    list_display = ('code', 'name', 'category', 'sale_price', 'current_stock_display', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'category')
        }),
        ('Financial Information', {
            'fields': ('sale_price',)
        }),
        ('Stock Information', {
            'fields': ('minimum_stock', 'maximum_stock'),
            'classes': ('collapse',)
        }),
        ('Physical Information', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def current_stock_display(self, obj):
        """Display current stock."""
        return obj.current_stock
    current_stock_display.short_description = 'Current Stock'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin interface for StockMovement model."""
    
    list_display = ('material', 'product', 'movement_type', 'quantity', 'created_at', 'document_number')
    list_filter = ('movement_type', 'reason', 'created_at', 'material__category', 'product__category')
    search_fields = ('material__name', 'product__name', 'document_number', 'notes')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('material', 'product', 'movement_type', 'reason', 'quantity')
        }),
        ('Cost Information', {
            'fields': ('unit_cost', 'total_cost'),
            'classes': ('collapse',)
        }),
        ('Reference Information', {
            'fields': ('document_number', 'production_order', 'sales_order', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
