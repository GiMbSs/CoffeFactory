"""
Testes para serializers da API
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from accounts.models import Employee
from inventory.models import Material, Product, UnitOfMeasure, Category
from production.models import Recipe, RecipeItem, ProductionOrder
from sales.models import Customer, SalesOrder, SalesOrderItem
from suppliers.models import Supplier
from financial.models import AccountsPayable, AccountsReceivable, Payroll

from api.serializers import (
    MaterialSerializer, ProductSerializer, RecipeSerializer,
    ProductionOrderSerializer, CustomerSerializer, SalesOrderSerializer,
    SupplierSerializer, AccountsPayableSerializer, AccountsReceivableSerializer,
    PayrollSerializer, EmployeeSerializer
)

User = get_user_model()


class SerializerTestCase(TestCase):
    """Base test case para serializers"""

    def setUp(self):
        """Setup comum para todos os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            position='Developer',
            department='IT',
            hire_date='2024-01-01',
            salary=Decimal('5000.00')
        )

        # Criar objetos de apoio
        self.unit_of_measure = UnitOfMeasure.objects.create(
            name='Quilograma',
            abbreviation='kg'
        )
        
        self.category = Category.objects.create(
            name='Matéria Prima',
            category_type='material'
        )

        self.material = Material.objects.create(
            name='Coffee Beans',
            code='MAT001',
            category=self.category,
            unit_of_measure=self.unit_of_measure,
            cost_per_unit=Decimal('25.00'),
            minimum_stock=100
        )

        self.product_category = Category.objects.create(
            name='Bebidas',
            category_type='product'
        )

        self.product = Product.objects.create(
            name='Espresso Coffee',
            code='PROD001',
            category=self.product_category,
            unit_of_measure=self.unit_of_measure,
            cost_per_unit=Decimal('10.00'),
            sale_price=Decimal('15.00'),
            minimum_stock=10
        )

        self.customer = Customer.objects.create(
            name='Test Customer',
            code='CUST001',
            customer_type='individual',
            email='customer@example.com',
            credit_limit=Decimal('1000.00')
        )

        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            code='SUPP001',
            supplier_type='individual',
            email='supplier@example.com',
            credit_limit=Decimal('5000.00')
        )


class InventorySerializersTest(SerializerTestCase):
    """Testes para serializers de estoque"""

    def test_material_serializer_valid_data(self):
        """Testa serializer de material com dados válidos"""
        data = {
            'name': 'Sugar',
            'code': 'MAT002',
            'category': self.category.id,
            'unit_of_measure': self.unit_of_measure.id,
            'cost_per_unit': '10.50',
            'minimum_stock': 50,
            'description': 'Sugar for coffee production',
            'status': 'active'
        }
        
        serializer = MaterialSerializer(data=data)
        print(f"Is valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
        else:
            print(f"Validated data: {serializer.validated_data}")
        
        self.assertTrue(serializer.is_valid())
        material = serializer.save()
        
        print(f"Created material - name: {material.name}, code: {material.code}")
        self.assertEqual(material.name, 'Sugar')
        self.assertEqual(material.code, 'MAT002')
        self.assertEqual(material.cost_per_unit, Decimal('10.50'))

    def test_material_serializer_invalid_stock(self):
        """Testa validação de estoque inválido"""
        data = {
            'name': 'Sugar',
            'code': 'MAT002',
            'unit_of_measure': 'kg',
            'unit_cost': '10.50',
            'minimum_stock': -10,  # Valor inválido
            'current_stock': 200
        }
        
        serializer = MaterialSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('minimum_stock', serializer.errors)

    def test_product_serializer_valid_data(self):
        """Testa serializer de produto com dados válidos"""
        data = {
            'name': 'Cappuccino',
            'code': 'PROD002',
            'description': 'Premium cappuccino coffee',
            'sale_price': '18.50',
            'cost_per_unit': '8.00',
            'minimum_stock': '10.00',
            'category': self.product_category.id,
            'unit_of_measure': self.unit_of_measure.id
        }
        
        serializer = ProductSerializer(data=data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        
        self.assertEqual(product.name, 'Cappuccino')
        self.assertEqual(product.sale_price, Decimal('18.50'))

    def test_product_serializer_negative_price(self):
        """Testa validação de preço negativo"""
        data = {
            'name': 'Cappuccino',
            'code': 'PROD002',
            'sale_price': '-10.00',  # Preço inválido
            'cost_per_unit': '8.00',
            'minimum_stock': '10.00',
            'category': self.category.id,
            'unit_of_measure': self.unit_of_measure.id
        }
        
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sale_price', serializer.errors)


class SalesSerializersTest(SerializerTestCase):
    """Testes para serializers de vendas"""

    def test_customer_serializer_valid_data(self):
        """Testa serializer de cliente com dados válidos"""
        data = {
            'name': 'New Customer',
            'trade_name': 'New Company Ltd',
            'customer_type': 'company',
            'email': 'new@example.com',
            'credit_limit': '2000.00'
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        customer = serializer.save()
        
        self.assertEqual(customer.name, 'New Customer')
        self.assertEqual(customer.credit_limit, Decimal('2000.00'))

    def test_customer_serializer_negative_credit(self):
        """Testa validação de limite de crédito negativo"""
        data = {
            'name': 'New Customer',
            'customer_type': 'individual',
            'email': 'new@example.com',
            'credit_limit': '-500.00'  # Valor inválido
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('credit_limit', serializer.errors)

    def test_sales_order_serializer_read_only_fields(self):
        """Testa campos somente leitura do serializer de pedido"""
        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            sales_representative=self.employee,
            payment_terms='30_days',
            delivery_date='2024-02-01'
        )
        
        serializer = SalesOrderSerializer(sales_order)
        data = serializer.data
        
        # Campos calculados devem estar presentes
        self.assertIn('customer_name', data)
        self.assertIn('sales_rep_name', data)
        self.assertIn('order_total', data)


class FinancialSerializersTest(SerializerTestCase):
    """Testes para serializers financeiros"""

    def test_accounts_payable_serializer_valid_data(self):
        """Testa serializer de contas a pagar com dados válidos"""
        data = {
            'invoice_number': 'INV001',
            'supplier': self.supplier.id,
            'expense_type': 'material_purchase',
            'original_amount': '500.00',
            'invoice_date': '2024-01-15',
            'due_date': '2024-02-15',
            'description': 'Purchase of raw materials'
        }
        
        serializer = AccountsPayableSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        payable = serializer.save(created_by=self.user)
        
        self.assertEqual(payable.invoice_number, 'INV001')
        self.assertEqual(payable.original_amount, Decimal('500.00'))

    def test_accounts_payable_serializer_zero_amount(self):
        """Testa validação de valor zero"""
        data = {
            'invoice_number': 'INV001',
            'supplier': self.supplier.id,
            'expense_type': 'material_purchase',
            'original_amount': '0.00',  # Valor inválido
            'invoice_date': '2024-01-15',
            'due_date': '2024-02-15'
        }
        
        serializer = AccountsPayableSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('original_amount', serializer.errors)

    def test_accounts_receivable_serializer_valid_data(self):
        """Testa serializer de contas a receber com dados válidos"""
        data = {
            'customer': self.customer.id,
            'invoice_number': 'REC001',
            'description': 'Coffee sales',
            'original_amount': '300.00',
            'issue_date': '2024-01-15',
            'due_date': '2024-02-15'
        }
        
        serializer = AccountsReceivableSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        receivable = serializer.save(created_by=self.user)
        
        self.assertEqual(receivable.original_amount, Decimal('300.00'))

    def test_payroll_serializer_valid_data(self):
        """Testa serializer de folha de pagamento"""
        data = {
            'employee': self.employee.id,
            'reference_month': '2024-01-01',
            'base_salary': '5000.00',
            'overtime_hours': '10.0',
            'days_worked': 22
        }
        
        serializer = PayrollSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        payroll = serializer.save(created_by=self.user)
        
        self.assertEqual(payroll.base_salary, Decimal('5000.00'))
        self.assertEqual(payroll.overtime_hours, Decimal('10.0'))

    def test_payroll_serializer_invalid_month(self):
        """Testa validação de mês inválido"""
        data = {
            'employee': self.employee.id,
            'reference_month': '2024-13-01',  # Mês inválido
            'base_salary': '5000.00',
            'days_worked': 22
        }
        
        serializer = PayrollSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('reference_month', serializer.errors)


class ProductionSerializersTest(SerializerTestCase):
    """Testes para serializers de produção"""

    def setUp(self):
        super().setUp()
        self.recipe = Recipe.objects.create(
            product=self.product,
            name='Espresso Recipe',
            yield_quantity=10,
            estimated_time_minutes=30
        )

    def test_recipe_serializer_valid_data(self):
        """Testa serializer de receita com dados válidos"""
        data = {
            'product': self.product.id,
            'code': 'REC002',
            'name': 'Cappuccino Recipe',
            'version': '2.0',
            'description': 'Recipe for cappuccino',
            'yield_quantity': 5,
            'estimated_time_minutes': 25,
            'status': 'active'
        }
        
        serializer = RecipeSerializer(data=data)
        if not serializer.is_valid():
            print(f"Recipe errors: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        recipe = serializer.save()
        
        self.assertEqual(recipe.name, 'Cappuccino Recipe')
        self.assertEqual(recipe.yield_quantity, 5)

    def test_recipe_serializer_zero_yield(self):
        """Testa validação de rendimento zero"""
        data = {
            'product': self.product.id,
            'code': 'REC003',
            'name': 'Invalid Recipe',
            'version': '1.0',
            'description': 'Invalid recipe test',
            'yield_quantity': 0,  # Valor inválido
            'estimated_time_minutes': 25,
            'status': 'active'
        }
        
        serializer = RecipeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('yield_quantity', serializer.errors)

    def test_production_order_serializer_valid_data(self):
        """Testa serializer de ordem de produção"""
        data = {
            'recipe': self.recipe.id,
            'supervisor': self.employee.id,
            'planned_quantity': 50,
            'priority': 'high',
            'planned_start_date': '2024-01-15T10:00:00Z',
            'planned_end_date': '2024-01-16T18:00:00Z'
        }
        
        serializer = ProductionOrderSerializer(data=data)
        if not serializer.is_valid():
            print(f"Production order errors: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        order = serializer.save(created_by=self.user)
        
        self.assertEqual(order.planned_quantity, 50)
        self.assertEqual(order.priority, 'high')


class SupplierSerializersTest(SerializerTestCase):
    """Testes para serializers de fornecedores"""

    def test_supplier_serializer_valid_data(self):
        """Testa serializer de fornecedor com dados válidos"""
        data = {
            'name': 'New Supplier',
            'supplier_type': 'company',
            'email': 'supplier@example.com',
            'credit_limit': '3000.00'
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        supplier = serializer.save()
        
        self.assertEqual(supplier.name, 'New Supplier')
        self.assertEqual(supplier.credit_limit, Decimal('3000.00'))

    def test_supplier_serializer_negative_credit(self):
        """Testa validação de limite de crédito negativo"""
        data = {
            'name': 'Invalid Supplier',
            'supplier_type': 'company',
            'email': 'invalid@example.com',
            'credit_limit': '-1000.00'  # Valor inválido
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('credit_limit', serializer.errors)


class EmployeeSerializersTest(SerializerTestCase):
    """Testes para serializers de funcionários"""

    def test_employee_serializer_read_only_fields(self):
        """Testa campos somente leitura do serializer de funcionário"""
        serializer = EmployeeSerializer(self.employee)
        data = serializer.data
        
        # Campos do usuário devem estar presentes
        self.assertIn('user', data)
        self.assertIn('employee_id', data)
        self.assertEqual(data['employee_id'], self.employee.employee_id)
