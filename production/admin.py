from django.contrib import admin
from .models import Recipe, RecipeItem, ProductionOrder, ProductionOrderItem


class RecipeItemInline(admin.TabularInline):
    """Inline admin for RecipeItem."""
    model = RecipeItem
    extra = 1
    fields = ('material', 'quantity', 'order', 'notes')
    ordering = ('order',)


class ProductionOrderItemInline(admin.TabularInline):
    """Inline admin for ProductionOrderItem."""
    model = ProductionOrderItem
    extra = 0
    fields = ('material', 'planned_quantity', 'consumed_quantity', 'unit_cost')
    readonly_fields = ('unit_cost',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin interface for Recipe model."""
    
    list_display = ('code', 'name', 'product', 'version', 'status', 'complexity', 'yield_quantity', 'estimated_time_minutes')
    list_filter = ('status', 'complexity', 'product__category', 'created_at')
    search_fields = ('code', 'name', 'product__name', 'description')
    ordering = ('code',)
    date_hierarchy = 'created_at'
    inlines = [RecipeItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'product', 'version', 'description')
        }),
        ('Production Information', {
            'fields': ('yield_quantity', 'estimated_time_minutes', 'complexity')
        }),
        ('Instructions', {
            'fields': ('instructions',),
            'classes': ('collapse',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    """Admin interface for RecipeItem model."""
    
    list_display = ('recipe', 'material', 'quantity', 'order')
    list_filter = ('recipe__status', 'material__category')
    search_fields = ('recipe__name', 'material__name')
    ordering = ('recipe', 'order')
    
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    """Admin interface for ProductionOrder model."""
    
    list_display = ('order_number', 'recipe', 'planned_quantity', 'produced_quantity', 'status', 'priority', 'planned_start_date', 'supervisor')
    list_filter = ('status', 'priority', 'planned_start_date', 'supervisor')
    search_fields = ('order_number', 'recipe__name', 'recipe__product__name')
    ordering = ('-planned_start_date',)
    date_hierarchy = 'planned_start_date'
    inlines = [ProductionOrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'recipe', 'planned_quantity', 'produced_quantity', 'status', 'priority')
        }),
        ('Planning', {
            'fields': ('planned_start_date', 'planned_end_date', 'supervisor')
        }),
        ('Execution', {
            'fields': ('actual_start_date', 'actual_end_date'),
            'classes': ('collapse',)
        }),
        ('Costs', {
            'fields': ('estimated_cost', 'actual_cost'),
            'classes': ('collapse',)
        }),
        ('Related Orders', {
            'fields': ('sales_order',),
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
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    actions = ['reserve_materials', 'start_production', 'complete_production']
    
    def reserve_materials(self, request, queryset):
        """Reserve materials for selected production orders."""
        count = 0
        for order in queryset.filter(status='approved'):
            try:
                order.reserve_materials()
                count += 1
            except ValueError as e:
                self.message_user(request, f'Error reserving materials for {order.order_number}: {e}', level='ERROR')
        
        if count > 0:
            self.message_user(request, f'{count} production orders had materials reserved.')
    reserve_materials.short_description = 'Reserve materials for selected orders'
    
    def start_production(self, request, queryset):
        """Start production for selected orders."""
        count = 0
        for order in queryset.filter(status='approved'):
            if order.can_start_production():
                order.status = 'in_progress'
                from django.utils import timezone
                order.actual_start_date = timezone.now()
                order.save()
                count += 1
        
        if count > 0:
            self.message_user(request, f'{count} production orders started.')
    start_production.short_description = 'Start production for selected orders'
    
    def complete_production(self, request, queryset):
        """Complete production for selected orders."""
        count = 0
        for order in queryset.filter(status='in_progress'):
            order.complete_production()
            count += 1
        
        if count > 0:
            self.message_user(request, f'{count} production orders completed.')
    complete_production.short_description = 'Complete production for selected orders'


@admin.register(ProductionOrderItem)
class ProductionOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for ProductionOrderItem model."""
    
    list_display = ('production_order', 'material', 'planned_quantity', 'consumed_quantity', 'unit_cost')
    list_filter = ('production_order__status', 'material__category')
    search_fields = ('production_order__order_number', 'material__name')
    ordering = ('production_order', 'material')
    
    readonly_fields = ('id', 'created_at', 'updated_at')
