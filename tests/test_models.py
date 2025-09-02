"""
Testes para modelos do Coffee Factory
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from accounts.models import Employee
from inventory.models import Material, Product, UnitOfMeasure, Category
from production.models import Recipe, RecipeItem, ProductionOrder
from sales.models import Customer, SalesOrder, SalesOrderItem
from suppliers.models import Supplier
from financial.models import AccountsPayable, AccountsReceivable, Payroll

User = get_user_model()


class ModelTestCase(TestCase):
    """Base test case com setup comum"""

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

        # Criar objetos de suporte
        self.unit_kg = UnitOfMeasure.objects.create(
            name='Kilogram',
            abbreviation='kg'
        )

        self.material_category = Category.objects.create(
            name='Raw Materials',
            category_type='material'
        )

        self.product_category = Category.objects.create(
            name='Beverages',
            category_type='product'
        )

        self.material = Material.objects.create(
            name='Coffee Beans',
            code='MAT001',
            unit_of_measure=self.unit_kg,
            category=self.material_category,
            cost_per_unit=Decimal('25.00'),
            minimum_stock=100
        )

        self.product = Product.objects.create(
            name='Espresso Coffee',
            code='PROD001',
            unit_of_measure=self.unit_kg,
            category=self.product_category,
            sale_price=Decimal('15.00'),
            cost_per_unit=Decimal('10.00'),
            minimum_stock=50
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


class InventoryModelsTest(ModelTestCase):
    """Testes para modelos de estoque"""

    def test_material_creation(self):
        """Testa criação de material"""
        self.assertEqual(self.material.name, 'Coffee Beans')
        self.assertEqual(self.material.code, 'MAT001')
        self.assertEqual(self.material.cost_per_unit, Decimal('25.00'))

    def test_material_stock_validation(self):
        """Testa validação de estoque mínimo"""
        material = Material(
            name='Test Material',
            code='MAT002',
            unit_of_measure=self.unit_kg,
            category=self.material_category,
            cost_per_unit=Decimal('10.00'),
            minimum_stock=-10,  # Valor inválido
        )
        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_product_creation(self):
        """Testa criação de produto"""
        self.assertEqual(self.product.name, 'Espresso Coffee')
        self.assertEqual(self.product.code, 'PROD001')
        self.assertEqual(self.product.sale_price, Decimal('15.00'))

    def test_product_unique_code(self):
        """Testa unicidade do código do produto"""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name='Another Product',
                code='PROD001',  # Código duplicado
                unit_of_measure=self.unit_kg,
                category=self.product_category,
                sale_price=Decimal('20.00'),
                cost_per_unit=Decimal('15.00'),
                minimum_stock=25
            )


class ProductionModelsTest(ModelTestCase):
    """Testes para modelos de produção"""

    def setUp(self):
        super().setUp()
        self.recipe = Recipe.objects.create(
            product=self.product,
            name='Espresso Recipe',
            yield_quantity=10,
            estimated_time_minutes=30
        )

    def test_recipe_creation(self):
        """Testa criação de receita"""
        self.assertEqual(self.recipe.product, self.product)
        self.assertEqual(self.recipe.name, 'Espresso Recipe')
        self.assertEqual(self.recipe.yield_quantity, 10)

    def test_recipe_item_creation(self):
        """Testa criação de item de receita"""
        recipe_item = RecipeItem.objects.create(
            recipe=self.recipe,
            material=self.material,
            quantity=Decimal('2.5')
        )
        self.assertEqual(recipe_item.recipe, self.recipe)
        self.assertEqual(recipe_item.material, self.material)
        self.assertEqual(recipe_item.quantity, Decimal('2.5'))

    def test_production_order_creation(self):
        """Testa criação de ordem de produção"""
        from datetime import datetime, timedelta
        start_date = datetime.now()
        end_date = start_date + timedelta(days=5)
        
        production_order = ProductionOrder.objects.create(
            recipe=self.recipe,
            planned_quantity=50,
            supervisor=self.employee,
            planned_start_date=start_date,
            planned_end_date=end_date,
            priority='medium',
            created_by=self.user
        )
        self.assertEqual(production_order.recipe, self.recipe)
        self.assertEqual(production_order.planned_quantity, 50)
        self.assertEqual(production_order.status, 'planned')  # Status padrão


class SalesModelsTest(ModelTestCase):
    """Testes para modelos de vendas"""

    def test_customer_creation(self):
        """Testa criação de cliente"""
        self.assertEqual(self.customer.name, 'Test Customer')
        self.assertEqual(self.customer.code, 'CUST001')
        self.assertEqual(self.customer.credit_limit, Decimal('1000.00'))

    def test_customer_available_credit(self):
        """Testa cálculo de crédito disponível"""
        # Cliente recém-criado deve ter todo o crédito disponível
        self.assertEqual(self.customer.available_credit, Decimal('1000.00'))

    def test_sales_order_creation(self):
        """Testa criação de pedido de venda"""
        from datetime import date, timedelta
        delivery_date = date.today() + timedelta(days=7)
        
        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            sales_representative=self.employee,
            delivery_date=delivery_date,
            payment_terms='30_days'
        )
        self.assertEqual(sales_order.customer, self.customer)
        self.assertEqual(sales_order.sales_representative, self.employee)
        self.assertEqual(sales_order.status, 'draft')  # Status padrão

    def test_sales_order_item_creation(self):
        """Testa criação de item de pedido"""
        from datetime import date, timedelta
        delivery_date = date.today() + timedelta(days=7)
        
        sales_order = SalesOrder.objects.create(
            customer=self.customer,
            sales_representative=self.employee,
            delivery_date=delivery_date,
            payment_terms='30_days'
        )
        
        sales_item = SalesOrderItem.objects.create(
            sales_order=sales_order,
            product=self.product,
            quantity=5,
            unit_price=Decimal('15.00')
        )
        
        self.assertEqual(sales_item.total_price, Decimal('75.00'))


class FinancialModelsTest(ModelTestCase):
    """Testes para modelos financeiros"""

    def test_accounts_payable_creation(self):
        """Testa criação de conta a pagar"""
        payable = AccountsPayable.objects.create(
            invoice_number='INV001',
            supplier=self.supplier,
            expense_type='material_purchase',
            original_amount=Decimal('500.00'),
            invoice_date='2024-01-15',
            due_date='2024-02-15',
            created_by=self.user
        )
        
        self.assertEqual(payable.invoice_number, 'INV001')
        self.assertEqual(payable.supplier, self.supplier)
        self.assertEqual(payable.original_amount, Decimal('500.00'))
        self.assertEqual(payable.status, 'pending')  # Status padrão

    def test_accounts_payable_balance(self):
        """Testa cálculo de saldo de conta a pagar"""
        payable = AccountsPayable.objects.create(
            invoice_number='INV001',
            supplier=self.supplier,
            expense_type='material_purchase',
            original_amount=Decimal('500.00'),
            invoice_date='2024-01-15',
            due_date='2024-02-15',
            created_by=self.user
        )
        
        # Sem pagamentos, saldo deve ser igual ao valor original
        self.assertEqual(payable.balance, Decimal('500.00'))
        
        # Após pagamento parcial
        payable.paid_amount = Decimal('200.00')
        payable.save()
        self.assertEqual(payable.balance, Decimal('300.00'))

    def test_accounts_receivable_creation(self):
        """Testa criação de conta a receber"""
        from datetime import date
        receivable = AccountsReceivable.objects.create(
            customer=self.customer,
            invoice_number='REC001',
            description='Coffee sales',
            original_amount=Decimal('300.00'),
            issue_date=date.today(),
            due_date=date.today(),
            created_by=self.user
        )
        
        self.assertEqual(receivable.customer, self.customer)
        self.assertEqual(receivable.original_amount, Decimal('300.00'))
        self.assertEqual(receivable.status, 'pending')

    def test_payroll_creation(self):
        """Testa criação de folha de pagamento"""
        from datetime import date
        payroll = Payroll.objects.create(
            employee=self.employee,
            reference_month=date(2024, 1, 1),
            base_salary=Decimal('5000.00'),
            overtime_hours=10,
            days_worked=22,
            hours_worked=Decimal('176.00'),
            created_by=self.user
        )
        
        # Processar folha de pagamento para calcular valores
        payroll.process_payroll()
        
        self.assertEqual(payroll.employee, self.employee)
        self.assertEqual(payroll.base_salary, Decimal('5000.00'))
        self.assertGreater(payroll.net_salary, Decimal('0'))  # Deve calcular salário líquido


class SupplierModelsTest(ModelTestCase):
    """Testes para modelos de fornecedores"""

    def test_supplier_creation(self):
        """Testa criação de fornecedor"""
        self.assertEqual(self.supplier.name, 'Test Supplier')
        self.assertEqual(self.supplier.code, 'SUPP001')
        self.assertEqual(self.supplier.credit_limit, Decimal('5000.00'))

    def test_supplier_unique_code(self):
        """Testa unicidade do código do fornecedor"""
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name='Another Supplier',
                code='SUPP001',  # Código duplicado
                supplier_type='individual',
                email='another@example.com'
            )


class EmployeeModelsTest(ModelTestCase):
    """Testes para modelos de funcionários"""

    def test_employee_creation(self):
        """Testa criação de funcionário"""
        self.assertEqual(self.employee.employee_id, 'EMP001')
        self.assertEqual(self.employee.position, 'Developer')
        self.assertEqual(self.employee.salary, Decimal('5000.00'))

    def test_employee_user_relationship(self):
        """Testa relacionamento com usuário"""
        self.assertEqual(self.employee.user, self.user)
        self.assertEqual(self.user.employee_profile, self.employee)
