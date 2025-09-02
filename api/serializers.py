"""
API Serializers for Coffee Factory Management System

This module contains Django REST Framework serializers for all models
in the Coffee Factory Management System. These serializers handle
the conversion between Python objects and JSON representations for
the API endpoints.

Following Django REST Framework best practices:
- Use ModelSerializer for standard CRUD operations
- Include proper field validation
- Handle nested relationships appropriately
- Provide read-only fields for calculated values
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

# Import all models
from accounts.models import Employee
from inventory.models import Category, Material, Product, StockMovement
from suppliers.models import Supplier
from production.models import Recipe, RecipeItem, ProductionOrder
from sales.models import Customer, SalesOrder, SalesOrderItem
from financial.models import AccountsPayable, AccountsReceivable, Payroll

User = get_user_model()


# ===========================================
# USER & EMPLOYEE SERIALIZERS
# ===========================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_email', 'employee_id', 'department',
            'position', 'employment_type', 'hire_date', 'salary', 
            'address', 'emergency_contact', 'emergency_phone', 'notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employee_id', 'age', 'created_at', 'updated_at']

    def get_age(self, obj):
        """Calculate employee age"""
        return obj.age

    def create(self, validated_data):
        """Create employee with user"""
        user_email = validated_data.pop('user_email')
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            # Create user if doesn't exist
            user = User.objects.create_user(
                email=user_email,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
        
        validated_data['user'] = user
        return super().create(validated_data)


# ===========================================
# INVENTORY SERIALIZERS
# ===========================================

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for Material model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_stock = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    
    class Meta:
        model = Material
        fields = [
            'id', 'code', 'name', 'description', 'category', 'category_name',
            'unit_of_measure', 'cost_per_unit', 'minimum_stock', 'maximum_stock',
            'status', 'current_stock', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_stock', 'created_at', 'updated_at']

    def validate_cost_per_unit(self, value):
        """Validate cost per unit is positive"""
        if value <= 0:
            raise serializers.ValidationError("Cost per unit must be greater than zero.")
        return value

    def validate_minimum_stock(self, value):
        """Validate minimum stock is not negative"""
        if value < 0:
            raise serializers.ValidationError("Minimum stock cannot be negative.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_stock = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'unit_of_measure', 'cost_per_unit', 'sale_price', 'minimum_stock',
            'current_stock', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_stock', 'created_at', 'updated_at']

    def validate_sale_price(self, value):
        """Validate sale price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Sale price must be greater than zero.")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    material_name = serializers.CharField(source='material.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'material', 'material_name', 'product', 'product_name',
            'movement_type', 'quantity', 'reference_document',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate that either material or product is specified, but not both"""
        material = data.get('material')
        product = data.get('product')
        
        if not material and not product:
            raise serializers.ValidationError("Either material or product must be specified.")
        
        if material and product:
            raise serializers.ValidationError("Cannot specify both material and product.")
        
        return data

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'code', 'name', 'trade_name', 'supplier_type',
            'cnpj_cpf', 'state_registration', 'municipal_registration',
            'email', 'phone', 'mobile', 'website',
            'address', 'address_number', 'address_complement', 'neighborhood',
            'city', 'state', 'postal_code', 'country',
            'contact_person', 'contact_email', 'contact_phone',
            'payment_terms', 'credit_limit', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def validate_credit_limit(self, value):
        """Validate credit limit is not negative"""
        if value and value < 0:
            raise serializers.ValidationError("Credit limit cannot be negative.")
        return value


# ===========================================
# PRODUCTION SERIALIZERS
# ===========================================

class RecipeItemSerializer(serializers.ModelSerializer):
    """Serializer for RecipeItem model"""
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_unit = serializers.CharField(source='material.unit_of_measure', read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeItem
        fields = [
            'id', 'recipe', 'material', 'material_name', 'material_unit',
            'quantity', 'total_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_cost', 'created_at', 'updated_at']

    def get_total_cost(self, obj):
        """Calculate total cost for this recipe item"""
        return obj.quantity * obj.material.cost_per_unit

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    items = RecipeItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'product', 'product_name', 'code', 'name', 'version',
            'description', 'yield_quantity', 'estimated_time_minutes', 
            'status', 'items', 'notes', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_yield_quantity(self, value):
        """Validate yield quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Yield quantity must be greater than zero.")
        return value


class ProductionOrderSerializer(serializers.ModelSerializer):
    """Serializer for ProductionOrder model"""
    recipe_name = serializers.CharField(source='recipe.name', read_only=True)
    product_name = serializers.CharField(source='recipe.product.name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.user.get_full_name', read_only=True)
    
    class Meta:
        model = ProductionOrder
        fields = [
            'id', 'order_number', 'recipe', 'recipe_name', 'product_name',
            'supervisor', 'supervisor_name', 'planned_quantity', 'produced_quantity',
            'status', 'priority', 'planned_start_date', 'planned_end_date',
            'actual_start_date', 'actual_end_date', 'estimated_cost', 'actual_cost',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'produced_quantity', 'actual_cost', 'created_at', 'updated_at']

    def get_total_cost(self, obj):
        """Calculate total cost for this production order"""
        return obj.total_cost

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        """Validate dates"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date.")
        
        return data


# ===========================================
# SALES SERIALIZERS
# ===========================================

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    available_credit = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'trade_name', 'cnpj_cpf', 'customer_type',
            'email', 'phone', 'address', 'credit_limit',
            'available_credit', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'available_credit', 'created_at', 'updated_at']

    def get_available_credit(self, obj):
        """Calculate available credit"""
        return obj.available_credit

    def validate_credit_limit(self, value):
        """Validate credit limit is not negative"""
        if value < 0:
            raise serializers.ValidationError("Credit limit cannot be negative.")
        return value


class SalesOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for SalesOrderItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    item_total = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesOrderItem
        fields = [
            'id', 'sales_order', 'product', 'product_name',
            'quantity', 'unit_price', 'item_total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'item_total', 'created_at', 'updated_at']

    def get_item_total(self, obj):
        """Calculate item total"""
        return obj.item_total

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_unit_price(self, value):
        """Validate unit price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for SalesOrder model"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sales_rep_name = serializers.CharField(source='sales_representative.user.get_full_name', read_only=True)
    items = SalesOrderItemSerializer(many=True, read_only=True)
    order_total = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesOrder
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'sales_representative', 'sales_rep_name', 'order_date', 'delivery_date',
            'status', 'payment_terms', 'discount_percentage',
            'order_total', 'items', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'order_total', 'created_at', 'updated_at']

    def get_order_total(self, obj):
        """Calculate order total"""
        return obj.total_amount

    def validate_discount_percentage(self, value):
        """Validate discount percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount percentage must be between 0 and 100.")
        return value

    def validate(self, data):
        """Validate dates"""
        order_date = data.get('order_date')
        delivery_date = data.get('delivery_date')
        
        if order_date and delivery_date and order_date > delivery_date:
            raise serializers.ValidationError("Order date must be before delivery date.")
        
        return data


# ===========================================
# FINANCIAL SERIALIZERS
# ===========================================

class AccountsPayableSerializer(serializers.ModelSerializer):
    """Serializer for AccountsPayable model"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountsPayable
        fields = [
            'id', 'supplier', 'supplier_name', 'invoice_number',
            'description', 'original_amount', 'invoice_date', 'due_date', 'payment_date',
            'paid_amount', 'status', 'expense_type', 'days_overdue', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'days_overdue', 'created_at', 'updated_at']

    def get_days_overdue(self, obj):
        """Calculate days overdue"""
        return obj.days_overdue

    def validate_original_amount(self, value):
        """Validate original amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Original amount must be greater than zero.")
        return value

    def validate_paid_amount(self, value):
        """Validate paid amount is not negative"""
        if value and value < 0:
            raise serializers.ValidationError("Paid amount cannot be negative.")
        return value


class AccountsReceivableSerializer(serializers.ModelSerializer):
    """Serializer for AccountsReceivable model"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountsReceivable
        fields = [
            'id', 'customer', 'customer_name', 'sales_order',
            'invoice_number', 'description', 'original_amount', 'issue_date', 'due_date',
            'payment_date', 'paid_amount', 'status', 'days_overdue',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'days_overdue', 'created_at', 'updated_at']

    def get_days_overdue(self, obj):
        """Calculate days overdue"""
        return obj.days_overdue

    def validate_original_amount(self, value):
        """Validate original amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Original amount must be greater than zero.")
        return value


class PayrollSerializer(serializers.ModelSerializer):
    """Serializer for Payroll model"""
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    net_salary = serializers.SerializerMethodField()
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'reference_month',
            'status', 'days_worked', 'hours_worked', 'overtime_hours',
            'base_salary', 'overtime_amount', 'bonus_amount',
            'commission_amount', 'other_earnings', 'gross_salary',
            'inss_amount', 'irrf_amount', 'health_insurance',
            'dental_insurance', 'meal_voucher_discount',
            'transport_voucher_discount', 'union_dues',
            'other_deductions', 'total_deductions', 'net_salary',
            'payment_date', 'payment_method', 'bank_account',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'gross_salary', 'total_deductions', 'net_salary',
            'created_at', 'updated_at'
        ]

    def get_net_salary(self, obj):
        """Get calculated net salary"""
        return obj.net_salary

    def validate_base_salary(self, value):
        """Validate base salary is positive"""
        if value <= 0:
            raise serializers.ValidationError("Base salary must be greater than zero.")
        return value

    def validate_overtime_hours(self, value):
        """Validate overtime hours is not negative"""
        if value < 0:
            raise serializers.ValidationError("Overtime hours cannot be negative.")
        return value

    def validate_reference_month(self, value):
        """Validate reference month is a valid date"""
        from datetime import date
        if isinstance(value, date):
            # Validate that it's the first day of a month
            if value.day != 1:
                raise serializers.ValidationError("Reference month must be the first day of the month.")
        return value
