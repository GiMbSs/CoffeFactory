"""
API Views for Coffee Factory Management System

This module contains Django REST Framework ViewSets for all models
in the Coffee Factory Management System. These views provide
standard CRUD operations and custom actions for the API endpoints.

Following Django REST Framework best practices:
- Use ViewSets for standard CRUD operations
- Implement proper filtering, ordering, and pagination
- Add custom actions where needed
- Include proper permissions and authentication
- Provide comprehensive documentation
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta

# Import models
from accounts.models import Employee
from inventory.models import Category, Material, Product, StockMovement
from suppliers.models import Supplier
from production.models import Recipe, RecipeItem, ProductionOrder
from sales.models import Customer, SalesOrder, SalesOrderItem
from financial.models import AccountsPayable, AccountsReceivable, Payroll

# Import serializers
from .serializers import (
    EmployeeSerializer, CategorySerializer, MaterialSerializer,
    ProductSerializer, StockMovementSerializer, SupplierSerializer,
    RecipeSerializer, RecipeItemSerializer, ProductionOrderSerializer,
    CustomerSerializer, SalesOrderSerializer, SalesOrderItemSerializer,
    AccountsPayableSerializer, AccountsReceivableSerializer,
    PayrollSerializer
)


# ===========================================
# BASE VIEWSET MIXIN
# ===========================================

class BaseViewSetMixin:
    """Base mixin for common ViewSet functionality"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """Override to add select_related/prefetch_related optimizations"""
        queryset = super().get_queryset()
        
        # Add common optimizations
        if hasattr(self.serializer_class.Meta.model, 'created_at'):
            queryset = queryset.order_by('-created_at')
            
        return queryset


# ===========================================
# USER & EMPLOYEE VIEWSETS
# ===========================================

class EmployeeViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Employee model"""
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeSerializer
    filterset_fields = ['department', 'position', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id']
    ordering_fields = ['user__first_name', 'hire_date', 'salary']
    ordering = ['-hire_date']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get employee statistics"""
        total_employees = self.get_queryset().count()
        active_employees = self.get_queryset().filter(is_active=True).count()
        departments = self.get_queryset().values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': total_employees - active_employees,
            'departments': list(departments)
        })

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get employees grouped by department"""
        department = request.query_params.get('department')
        queryset = self.get_queryset()
        
        if department:
            queryset = queryset.filter(department=department)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ===========================================
# INVENTORY VIEWSETS
# ===========================================

class CategoryViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Category model"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        """Get all materials in this category"""
        category = self.get_object()
        materials = Material.objects.filter(category=category)
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in this category"""
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class MaterialViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Material model"""
    queryset = Material.objects.select_related('category').all()
    serializer_class = MaterialSerializer
    filterset_fields = ['category', 'is_active', 'unit_of_measure']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'unit_cost', 'current_stock', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get materials with low stock"""
        materials = self.get_queryset().filter(
            current_stock__lte=F('minimum_stock')
        )
        serializer = self.get_serializer(materials, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for this material"""
        material = self.get_object()
        movements = StockMovement.objects.filter(material=material).order_by('-created_at')
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get material statistics"""
        queryset = self.get_queryset()
        total_materials = queryset.count()
        active_materials = queryset.filter(is_active=True).count()
        low_stock_materials = queryset.filter(
            current_stock__lte=F('minimum_stock')
        ).count()
        
        return Response({
            'total_materials': total_materials,
            'active_materials': active_materials,
            'low_stock_materials': low_stock_materials,
            'total_value': queryset.aggregate(
                total=Sum(F('current_stock') * F('unit_cost'))
            )['total'] or 0
        })


class ProductViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Product model"""
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'is_active', 'unit_of_measure']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'sale_price', 'current_stock', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = self.get_queryset().filter(
            current_stock__lte=F('minimum_stock')
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for this product"""
        product = self.get_object()
        movements = StockMovement.objects.filter(product=product).order_by('-created_at')
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def recipes(self, request, pk=None):
        """Get recipes for this product"""
        product = self.get_object()
        recipes = Recipe.objects.filter(product=product)
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)


class StockMovementViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for StockMovement model"""
    queryset = StockMovement.objects.select_related('material', 'product').all()
    serializer_class = StockMovementSerializer
    filterset_fields = ['movement_type', 'material', 'product']
    search_fields = ['reference_document', 'notes']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get movements by date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ===========================================
# SUPPLIER VIEWSETS
# ===========================================

class SupplierViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Supplier model"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ['supplier_type', 'is_active', 'city', 'state']
    search_fields = ['name', 'trade_name', 'cnpj_cpf', 'email', 'contact_person']
    ordering_fields = ['name', 'trade_name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get supplier statistics"""
        queryset = self.get_queryset()
        total_suppliers = queryset.count()
        active_suppliers = queryset.filter(is_active=True).count()
        by_type = queryset.values('supplier_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_suppliers': total_suppliers,
            'active_suppliers': active_suppliers,
            'supplier_types': list(by_type)
        })


# ===========================================
# PRODUCTION VIEWSETS
# ===========================================

class RecipeViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Recipe model"""
    queryset = Recipe.objects.select_related('product').prefetch_related('recipe_items__material').all()
    serializer_class = RecipeSerializer
    filterset_fields = ['product', 'is_active']
    search_fields = ['name', 'description', 'product__name']
    ordering_fields = ['name', 'total_cost', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a recipe"""
        original_recipe = self.get_object()
        
        # Create new recipe
        new_recipe_data = {
            'product': original_recipe.product.id,
            'name': f"{original_recipe.name} (Copy)",
            'description': original_recipe.description,
            'yield_quantity': original_recipe.yield_quantity,
            'preparation_time': original_recipe.preparation_time,
        }
        
        serializer = self.get_serializer(data=new_recipe_data)
        if serializer.is_valid():
            new_recipe = serializer.save()
            
            # Copy recipe items
            for item in original_recipe.items.all():
                RecipeItem.objects.create(
                    recipe=new_recipe,
                    material=item.material,
                    quantity=item.quantity
                )
            
            # Return the complete recipe with items
            complete_serializer = self.get_serializer(new_recipe)
            return Response(complete_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductionOrderViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for ProductionOrder model"""
    queryset = ProductionOrder.objects.select_related('recipe__product').all()
    serializer_class = ProductionOrderSerializer
    filterset_fields = ['status', 'priority', 'recipe', 'recipe__product']
    search_fields = ['order_number', 'recipe__name', 'notes']
    ordering_fields = ['order_number', 'start_date', 'priority', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def start_production(self, request, pk=None):
        """Start production order"""
        production_order = self.get_object()
        
        if production_order.status != 'pending':
            return Response(
                {'error': 'Production order must be in pending status to start'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            production_order.start_production()
            serializer = self.get_serializer(production_order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        """Complete production order"""
        production_order = self.get_object()
        
        if production_order.status != 'in_progress':
            return Response(
                {'error': 'Production order must be in progress to complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        production_order.complete_production()
        serializer = self.get_serializer(production_order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get production statistics"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        this_month = queryset.filter(
            created_at__year=today.year,
            created_at__month=today.month
        )
        
        return Response({
            'total_orders': queryset.count(),
            'by_status': list(by_status),
            'this_month': this_month.count(),
            'completed_this_month': this_month.filter(status='completed').count()
        })


# ===========================================
# SALES VIEWSETS
# ===========================================

class CustomerViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Customer model"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ['customer_type', 'is_active']
    search_fields = ['name', 'company_name', 'cpf_cnpj', 'email']
    ordering_fields = ['name', 'company_name', 'credit_limit', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get customer statistics"""
        queryset = self.get_queryset()
        total_customers = queryset.count()
        active_customers = queryset.filter(is_active=True).count()
        by_type = queryset.values('customer_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_customers': total_customers,
            'active_customers': active_customers,
            'customer_types': list(by_type),
            'total_credit_limit': queryset.aggregate(
                total=Sum('credit_limit')
            )['total'] or 0
        })

    @action(detail=True, methods=['get'])
    def sales_history(self, request, pk=None):
        """Get sales history for customer"""
        customer = self.get_object()
        orders = SalesOrder.objects.filter(customer=customer).order_by('-created_at')
        serializer = SalesOrderSerializer(orders, many=True)
        return Response(serializer.data)


class SalesOrderViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for SalesOrder model"""
    queryset = SalesOrder.objects.select_related('customer', 'sales_representative__user').prefetch_related('order_items__product').all()
    serializer_class = SalesOrderSerializer
    filterset_fields = ['status', 'customer', 'sales_representative']
    search_fields = ['order_number', 'customer__name', 'notes']
    ordering_fields = ['order_number', 'order_date', 'total_amount', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm sales order"""
        sales_order = self.get_object()
        
        if sales_order.status != 'pending':
            return Response(
                {'error': 'Sales order must be in pending status to confirm'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sales_order.status = 'confirmed'
        sales_order.save()
        
        serializer = self.get_serializer(sales_order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get sales statistics"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        this_month = queryset.filter(
            order_date__year=today.year,
            order_date__month=today.month
        )
        
        by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_orders': queryset.count(),
            'by_status': list(by_status),
            'this_month_orders': this_month.count(),
            'this_month_total': this_month.aggregate(
                total=Sum('order_total')
            )['total'] or 0
        })


class SalesOrderItemViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for SalesOrderItem model"""
    queryset = SalesOrderItem.objects.select_related('sales_order', 'product').all()
    serializer_class = SalesOrderItemSerializer
    filterset_fields = ['sales_order', 'product']
    search_fields = ['product__name', 'sales_order__order_number']
    ordering_fields = ['quantity', 'unit_price', 'item_total', 'created_at']
    ordering = ['-created_at']


# ===========================================
# FINANCIAL VIEWSETS
# ===========================================

class AccountsPayableViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for AccountsPayable model"""
    queryset = AccountsPayable.objects.select_related('supplier').all()
    serializer_class = AccountsPayableSerializer
    filterset_fields = ['status', 'supplier']
    search_fields = ['document_number', 'description', 'supplier__name']
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['due_date']

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue accounts payable"""
        overdue = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status='pending'
        )
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get accounts payable statistics"""
        queryset = self.get_queryset()
        pending = queryset.filter(status='pending')
        overdue = pending.filter(due_date__lt=timezone.now().date())
        
        return Response({
            'total_payable': pending.aggregate(total=Sum('original_amount'))['total'] or 0,
            'overdue_amount': overdue.aggregate(total=Sum('original_amount'))['total'] or 0,
            'overdue_count': overdue.count(),
            'pending_count': pending.count()
        })


class AccountsReceivableViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for AccountsReceivable model"""
    queryset = AccountsReceivable.objects.select_related('customer', 'sales_order').all()
    serializer_class = AccountsReceivableSerializer
    filterset_fields = ['status', 'customer']
    search_fields = ['document_number', 'description', 'customer__name']
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['due_date']

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue accounts receivable"""
        overdue = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status='pending'
        )
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get accounts receivable statistics"""
        queryset = self.get_queryset()
        pending = queryset.filter(status='pending')
        overdue = pending.filter(due_date__lt=timezone.now().date())
        
        return Response({
            'total_receivable': pending.aggregate(total=Sum('original_amount'))['total'] or 0,
            'overdue_amount': overdue.aggregate(total=Sum('original_amount'))['total'] or 0,
            'overdue_count': overdue.count(),
            'pending_count': pending.count()
        })


class PayrollViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Payroll model"""
    queryset = Payroll.objects.select_related('employee__user').all()
    serializer_class = PayrollSerializer
    filterset_fields = ['status', 'reference_month', 'reference_year', 'employee']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['reference_year', 'reference_month', 'base_salary', 'created_at']
    ordering = ['-reference_year', '-reference_month']

    @action(detail=False, methods=['get'])
    def by_period(self, request):
        """Get payroll by period"""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = self.get_queryset()
        
        if month:
            queryset = queryset.filter(reference_month=month)
        if year:
            queryset = queryset.filter(reference_year=year)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get payroll statistics"""
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        current_payroll = self.get_queryset().filter(
            reference_month=current_month,
            reference_year=current_year
        )
        
        return Response({
            'current_month_total': current_payroll.aggregate(
                total=Sum('net_salary')
            )['total'] or 0,
            'current_month_count': current_payroll.count(),
            'processed_count': current_payroll.filter(status='paid').count(),
            'pending_count': current_payroll.filter(status='pending').count()
        })
