"""
Testes para views da API
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import Employee
from inventory.models import Material, Product, UnitOfMeasure, Category
from production.models import Recipe, ProductionOrder
from sales.models import Customer, SalesOrder
from suppliers.models import Supplier
from financial.models import AccountsPayable, AccountsReceivable, Payroll

User = get_user_model()


class APIViewTestCase(APITestCase):
    """Base test case para views da API"""

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
            department='sales',  # Mudando para 'sales' para corresponder ao limit_choices_to
            hire_date='2024-01-01',
            salary=Decimal('5000.00')
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Objetos necessários
        self.unit_of_measure = UnitOfMeasure.objects.create(
            name='Quilograma',
            abbreviation='kg',
            description='Unidade de medida de peso'
        )
        
        self.category = Category.objects.create(
            name='Matéria Prima',
            description='Materiais para produção',
            category_type='material'
        )

        # Dados de teste
        self.material = Material.objects.create(
            name='Coffee Beans',
            code='MAT001',
            description='Grãos de café para produção',
            unit_of_measure=self.unit_of_measure,
            category=self.category,
            cost_per_unit=Decimal('25.00'),
            minimum_stock=100,
            status='active'
        )

        self.product_category = Category.objects.create(
            name='Bebidas',
            description='Produtos finalizados - bebidas',
            category_type='product'
        )

        self.product = Product.objects.create(
            name='Espresso Coffee',
            code='PROD001',
            description='Café expresso premium',
            unit_of_measure=self.unit_of_measure,
            category=self.product_category,
            cost_per_unit=Decimal('10.00'),
            sale_price=Decimal('15.00'),
            minimum_stock=50,
            status='active'
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


class InventoryAPITest(APIViewTestCase):
    """Testes para API de estoque"""

    def test_material_list(self):
        """Testa listagem de materiais"""
        url = reverse('api:material-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Coffee Beans')

    def test_material_create(self):
        """Testa criação de material via API"""
        url = reverse('api:material-list')
        data = {
            'name': 'Sugar',
            'code': 'MAT002',
            'description': 'Sugar for coffee production',
            'category': self.category.id,
            'unit_of_measure': self.unit_of_measure.id,
            'cost_per_unit': '10.50',
            'minimum_stock': 50,
            'status': 'active'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 2)

    def test_material_detail(self):
        """Testa detalhes de material"""
        url = reverse('api:material-detail', kwargs={'pk': self.material.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Coffee Beans')

    def test_material_update(self):
        """Testa atualização de material"""
        url = reverse('api:material-detail', kwargs={'pk': self.material.pk})
        data = {
            'name': 'Premium Coffee Beans',
            'code': 'MAT001',
            'description': 'Premium coffee beans for production',
            'category': self.category.id,
            'unit_of_measure': self.unit_of_measure.id,
            'cost_per_unit': '30.00',
            'minimum_stock': 100,
            'status': 'active'
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.material.refresh_from_db()
        self.assertEqual(self.material.name, 'Premium Coffee Beans')
        self.assertEqual(self.material.cost_per_unit, Decimal('30.00'))

    def test_material_delete(self):
        """Testa exclusão de material"""
        url = reverse('api:material-detail', kwargs={'pk': self.material.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Material.objects.count(), 0)

    def test_product_list(self):
        """Testa listagem de produtos"""
        url = reverse('api:product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_create(self):
        """Testa criação de produto"""
        url = reverse('api:product-list')
        data = {
            'name': 'Cappuccino',
            'code': 'PROD002',
            'description': 'Delicious cappuccino',
            'category': self.product_category.id,
            'unit_of_measure': self.unit_of_measure.id,
            'cost_per_unit': '15.00',
            'sale_price': '18.50',
            'minimum_stock': 10,
            'status': 'active'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SalesAPITest(APIViewTestCase):
    """Testes para API de vendas"""

    def test_customer_list(self):
        """Testa listagem de clientes"""
        url = reverse('api:customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_customer_create(self):
        """Testa criação de cliente"""
        url = reverse('api:customer-list')
        data = {
            'name': 'New Customer',
            'customer_type': 'individual',
            'email': 'new@example.com',
            'credit_limit': '1500.00'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

    def test_sales_order_create(self):
        """Testa criação de pedido de venda"""
        url = reverse('api:salesorder-list')
        data = {
            'customer': self.customer.id,
            'sales_representative': self.employee.id,
            'payment_terms': '30_days',
            'delivery_date': '2024-02-15',
            'order_date': '2024-01-15',
            'status': 'draft',
            'priority': 'normal'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FinancialAPITest(APIViewTestCase):
    """Testes para API financeira"""

    def test_accounts_payable_list(self):
        """Testa listagem de contas a pagar"""
        # Criar uma conta a pagar
        payable = AccountsPayable.objects.create(
            invoice_number='INV001',
            supplier=self.supplier,
            expense_type='material_purchase',
            original_amount=Decimal('500.00'),
            invoice_date='2024-01-15',
            due_date='2024-02-15',
            created_by=self.user
        )
        
        url = reverse('api:accountspayable-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_accounts_payable_create(self):
        """Testa criação de conta a pagar"""
        url = reverse('api:accountspayable-list')
        data = {
            'invoice_number': 'INV002',
            'supplier': self.supplier.id,
            'expense_type': 'material_purchase',
            'original_amount': '750.00',
            'invoice_date': '2024-01-20',
            'due_date': '2024-02-20',
            'description': 'Material purchase',
            'status': 'pending'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accounts_payable_statistics(self):
        """Testa endpoint de estatísticas de contas a pagar"""
        # Criar contas a pagar
        AccountsPayable.objects.create(
            invoice_number='INV001',
            supplier=self.supplier,
            expense_type='material_purchase',
            original_amount=Decimal('500.00'),
            invoice_date='2024-01-15',
            due_date='2024-02-15',
            status='pending',
            created_by=self.user
        )
        
        url = reverse('api:accountspayable-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_payable', response.data)
        self.assertIn('pending_count', response.data)

    def test_accounts_receivable_list(self):
        """Testa listagem de contas a receber"""
        # Criar uma conta a receber
        receivable = AccountsReceivable.objects.create(
            customer=self.customer,
            invoice_number='REC001',
            description='Coffee sales',
            original_amount=Decimal('300.00'),
            issue_date='2024-01-15',
            due_date='2024-02-15',
            created_by=self.user
        )
        
        url = reverse('api:accountsreceivable-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_payroll_create(self):
        """Testa criação de folha de pagamento"""
        url = reverse('api:payroll-list')
        data = {
            'employee': self.employee.id,
            'reference_month': '2024-01-01',
            'base_salary': '5000.00',
            'overtime_hours': 8,
            'days_worked': 22,
            'hours_worked': '176.00'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProductionAPITest(APIViewTestCase):
    """Testes para API de produção"""

    def setUp(self):
        super().setUp()
        self.recipe = Recipe.objects.create(
            product=self.product,
            name='Espresso Recipe',
            yield_quantity=10,
            estimated_time_minutes=30
        )

    def test_recipe_list(self):
        """Testa listagem de receitas"""
        url = reverse('api:recipe-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_recipe_create(self):
        """Testa criação de receita"""
        url = reverse('api:recipe-list')
        data = {
            'product': self.product.id,
            'name': 'Cappuccino Recipe',
            'code': 'REC002',
            'description': 'Recipe for cappuccino',
            'yield_quantity': 5,
            'estimated_time_minutes': 15,
            'status': 'active',
            'version': '2.0'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_production_order_create(self):
        """Testa criação de ordem de produção"""
        url = reverse('api:productionorder-list')
        data = {
            'recipe': self.recipe.id,
            'supervisor': self.employee.id,
            'planned_quantity': 50,
            'priority': 'high',
            'status': 'planned',
            'planned_start_date': '2024-01-20T08:00:00Z',
            'planned_end_date': '2024-01-22T17:00:00Z'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SupplierAPITest(APIViewTestCase):
    """Testes para API de fornecedores"""

    def test_supplier_list(self):
        """Testa listagem de fornecedores"""
        url = reverse('api:supplier-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_supplier_create(self):
        """Testa criação de fornecedor"""
        url = reverse('api:supplier-list')
        data = {
            'name': 'New Supplier',
            'supplier_type': 'company',
            'email': 'new_supplier@example.com',
            'credit_limit': '3000.00'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticationTest(APITestCase):
    """Testes para autenticação da API"""

    def test_unauthenticated_access(self):
        """Testa acesso não autenticado"""
        client = APIClient()
        url = reverse('api:material-list')
        response = client.get(url)
        
        # Dependendo da configuração, pode retornar 401 ou 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_access(self):
        """Testa acesso autenticado"""
        user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('api:material-list')
        response = client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
