#!/usr/bin/env python
"""
Script de populate para demonstração do Coffee Factory Management System.
Este script cria dados de demonstração para todos os módulos do sistema.

Para executar:
python manage.py shell
exec(open('scripts/populate_demo_data.py').read())

Ou:
python scripts/populate_demo_data.py
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_factory.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import Employee
from inventory.models import Category, UnitOfMeasure, Material, Product
from suppliers.models import Supplier
from sales.models import Customer, SalesOrder, SalesOrderItem
from financial.models import AccountsPayable, AccountsReceivable
from production.models import Recipe, RecipeItem, ProductionOrder, ProductionOrderItem

User = get_user_model()

class DemoDataPopulator:
    """Classe para popular dados de demonstração."""
    
    def __init__(self):
        self.created_data = {
            'users': 0,
            'employees': 0,
            'categories': 0,
            'units': 0,
            'materials': 0,
            'products': 0,
            'suppliers': 0,
            'customers': 0,
            'sales_orders': 0,
            'accounts_payable': 0,
            'accounts_receivable': 0,
            'recipes': 0,
            'production_orders': 0,
        }
    
    def run(self):
        """Executa o populate completo."""
        print("🚀 Iniciando populate de dados de demonstração...")
        print("=" * 60)
        
        # Ordem de criação (respeitando dependências)
        self.create_users()
        self.create_employees()
        self.create_categories()
        self.create_units_of_measure()
        self.create_materials()
        self.create_products()
        self.create_suppliers()
        self.create_customers()
        self.create_sales_orders()
        self.create_accounts_payable()
        self.create_accounts_receivable()
        self.create_recipes()
        self.create_production_orders()
        
        self.print_summary()
    
    def create_users(self):
        """Cria usuários de demonstração."""
        print("👥 Criando usuários...")
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@coffeefactory.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'vendedor1',
                'email': 'vendas1@coffeefactory.com',
                'first_name': 'João',
                'last_name': 'Silva',
                'is_staff': True,
            },
            {
                'username': 'vendedor2',
                'email': 'vendas2@coffeefactory.com',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'is_staff': True,
            },
            {
                'username': 'producao1',
                'email': 'producao1@coffeefactory.com',
                'first_name': 'Carlos',
                'last_name': 'Oliveira',
                'is_staff': True,
            },
            {
                'username': 'financeiro1',
                'email': 'financeiro1@coffeefactory.com',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'is_staff': True,
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.created_data['users'] += 1
                print(f"  ✅ Usuário criado: {user.username}")
            else:
                print(f"  ℹ️  Usuário já existe: {user.username}")
    
    def create_employees(self):
        """Cria funcionários de demonstração."""
        print("\n👨‍💼 Criando funcionários...")
        
        employees_data = [
            {
                'code': 'JOASIL001',
                'first_name': 'João',
                'last_name': 'Silva',
                'email': 'joao.silva@coffeefactory.com',
                'phone': '+5511987654321',
                'department': 'sales',
                'position': 'Vendedor Senior',
                'hire_date': date(2023, 1, 15),
                'salary': Decimal('4500.00'),
            },
            {
                'code': 'MARSAN002',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'email': 'maria.santos@coffeefactory.com',
                'phone': '+5511987654322',
                'department': 'sales',
                'position': 'Vendedora',
                'hire_date': date(2023, 3, 10),
                'salary': Decimal('3800.00'),
            },
            {
                'code': 'CAROLI003',
                'first_name': 'Carlos',
                'last_name': 'Oliveira',
                'email': 'carlos.oliveira@coffeefactory.com',
                'phone': '+5511987654323',
                'department': 'production',
                'position': 'Supervisor de Produção',
                'hire_date': date(2022, 8, 20),
                'salary': Decimal('5200.00'),
            },
            {
                'code': 'ANACOS004',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'email': 'ana.costa@coffeefactory.com',
                'phone': '+5511987654324',
                'department': 'financial',
                'position': 'Analista Financeiro',
                'hire_date': date(2023, 5, 1),
                'salary': Decimal('4200.00'),
            },
            {
                'code': 'PEDLIM005',
                'first_name': 'Pedro',
                'last_name': 'Lima',
                'email': 'pedro.lima@coffeefactory.com',
                'phone': '+5511987654325',
                'department': 'production',
                'position': 'Operador de Produção',
                'hire_date': date(2023, 7, 12),
                'salary': Decimal('3200.00'),
            },
        ]
        
        for emp_data in employees_data:
            employee, created = Employee.objects.get_or_create(
                code=emp_data['code'],
                defaults=emp_data
            )
            if created:
                self.created_data['employees'] += 1
                print(f"  ✅ Funcionário criado: {employee.first_name} {employee.last_name}")
    
    def create_categories(self):
        """Cria categorias de produtos."""
        print("\n📁 Criando categorias...")
        
        categories_data = [
            {
                'name': 'Café Torrado',
                'description': 'Cafés torrados em diferentes níveis'
            },
            {
                'name': 'Café Verde',
                'description': 'Grãos de café verde para torrefação'
            },
            {
                'name': 'Embalagens',
                'description': 'Materiais de embalagem'
            },
            {
                'name': 'Acessórios',
                'description': 'Acessórios para café'
            },
            {
                'name': 'Especiais',
                'description': 'Cafés especiais e gourmet'
            },
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.created_data['categories'] += 1
                print(f"  ✅ Categoria criada: {category.name}")
    
    def create_units_of_measure(self):
        """Cria unidades de medida."""
        print("\n📏 Criando unidades de medida...")
        
        units_data = [
            {'name': 'Quilograma', 'symbol': 'kg', 'description': 'Quilograma'},
            {'name': 'Grama', 'symbol': 'g', 'description': 'Grama'},
            {'name': 'Litro', 'symbol': 'L', 'description': 'Litro'},
            {'name': 'Unidade', 'symbol': 'un', 'description': 'Unidade'},
            {'name': 'Pacote', 'symbol': 'pct', 'description': 'Pacote'},
            {'name': 'Caixa', 'symbol': 'cx', 'description': 'Caixa'},
            {'name': 'Saco', 'symbol': 'sc', 'description': 'Saco'},
        ]
        
        for unit_data in units_data:
            unit, created = UnitOfMeasure.objects.get_or_create(
                symbol=unit_data['symbol'],
                defaults=unit_data
            )
            if created:
                self.created_data['units'] += 1
                print(f"  ✅ Unidade criada: {unit.name} ({unit.symbol})")
    
    def create_materials(self):
        """Cria materiais de estoque."""
        print("\n🏭 Criando materiais...")
        
        # Obter unidades criadas
        kg = UnitOfMeasure.objects.get(symbol='kg')
        un = UnitOfMeasure.objects.get(symbol='un')
        
        # Obter categorias
        cafe_verde = Category.objects.get(name='Café Verde')
        embalagens = Category.objects.get(name='Embalagens')
        
        materials_data = [
            {
                'code': 'MAT001',
                'name': 'Café Verde Arábica Premium',
                'description': 'Grãos de café verde arábica premium',
                'category': cafe_verde,
                'unit_of_measure': kg,
                'cost_price': Decimal('18.50'),
                'current_stock': Decimal('500.00'),
                'minimum_stock': Decimal('50.00'),
                'maximum_stock': Decimal('1000.00'),
            },
            {
                'code': 'MAT002',
                'name': 'Café Verde Robusta',
                'description': 'Grãos de café verde robusta',
                'category': cafe_verde,
                'unit_of_measure': kg,
                'cost_price': Decimal('12.00'),
                'current_stock': Decimal('300.00'),
                'minimum_stock': Decimal('30.00'),
                'maximum_stock': Decimal('600.00'),
            },
            {
                'code': 'MAT003',
                'name': 'Embalagem 250g',
                'description': 'Embalagem vácuo 250g',
                'category': embalagens,
                'unit_of_measure': un,
                'cost_price': Decimal('0.85'),
                'current_stock': Decimal('2000.00'),
                'minimum_stock': Decimal('200.00'),
                'maximum_stock': Decimal('5000.00'),
            },
            {
                'code': 'MAT004',
                'name': 'Embalagem 500g',
                'description': 'Embalagem vácuo 500g',
                'category': embalagens,
                'unit_of_measure': un,
                'cost_price': Decimal('1.20'),
                'current_stock': Decimal('1500.00'),
                'minimum_stock': Decimal('150.00'),
                'maximum_stock': Decimal('3000.00'),
            },
            {
                'code': 'MAT005',
                'name': 'Embalagem 1kg',
                'description': 'Embalagem vácuo 1kg',
                'category': embalagens,
                'unit_of_measure': un,
                'cost_price': Decimal('1.85'),
                'current_stock': Decimal('800.00'),
                'minimum_stock': Decimal('80.00'),
                'maximum_stock': Decimal('2000.00'),
            },
        ]
        
        for mat_data in materials_data:
            material, created = Material.objects.get_or_create(
                code=mat_data['code'],
                defaults=mat_data
            )
            if created:
                self.created_data['materials'] += 1
                print(f"  ✅ Material criado: {material.name}")
    
    def create_products(self):
        """Cria produtos finais."""
        print("\n☕ Criando produtos...")
        
        # Obter unidades e categorias
        un = UnitOfMeasure.objects.get(symbol='un')
        cafe_torrado = Category.objects.get(name='Café Torrado')
        especiais = Category.objects.get(name='Especiais')
        
        products_data = [
            {
                'code': 'PROD001',
                'name': 'Café Gourmet 250g',
                'description': 'Café gourmet torrado e moído 250g',
                'category': cafe_torrado,
                'unit_of_measure': un,
                'cost_price': Decimal('15.50'),
                'sale_price': Decimal('25.90'),
                'current_stock': Decimal('150.00'),
                'minimum_stock': Decimal('20.00'),
                'maximum_stock': Decimal('500.00'),
            },
            {
                'code': 'PROD002',
                'name': 'Café Premium 500g',
                'description': 'Café premium torrado e moído 500g',
                'category': cafe_torrado,
                'unit_of_measure': un,
                'cost_price': Decimal('28.00'),
                'sale_price': Decimal('45.00'),
                'current_stock': Decimal('80.00'),
                'minimum_stock': Decimal('15.00'),
                'maximum_stock': Decimal('300.00'),
            },
            {
                'code': 'PROD003',
                'name': 'Café Especial 1kg',
                'description': 'Café especial torrado e moído 1kg',
                'category': especiais,
                'unit_of_measure': un,
                'cost_price': Decimal('52.00'),
                'sale_price': Decimal('85.00'),
                'current_stock': Decimal('40.00'),
                'minimum_stock': Decimal('10.00'),
                'maximum_stock': Decimal('150.00'),
            },
            {
                'code': 'PROD004',
                'name': 'Café Tradicional 250g',
                'description': 'Café tradicional torrado e moído 250g',
                'category': cafe_torrado,
                'unit_of_measure': un,
                'cost_price': Decimal('8.50'),
                'sale_price': Decimal('15.90'),
                'current_stock': Decimal('200.00'),
                'minimum_stock': Decimal('30.00'),
                'maximum_stock': Decimal('800.00'),
            },
            {
                'code': 'PROD005',
                'name': 'Café Orgânico 500g',
                'description': 'Café orgânico certificado 500g',
                'category': especiais,
                'unit_of_measure': un,
                'cost_price': Decimal('35.00'),
                'sale_price': Decimal('55.00'),
                'current_stock': Decimal('60.00'),
                'minimum_stock': Decimal('12.00'),
                'maximum_stock': Decimal('200.00'),
            },
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                code=prod_data['code'],
                defaults=prod_data
            )
            if created:
                self.created_data['products'] += 1
                print(f"  ✅ Produto criado: {product.name}")
    
    def create_suppliers(self):
        """Cria fornecedores."""
        print("\n🏢 Criando fornecedores...")
        
        suppliers_data = [
            {
                'code': 'FORN001',
                'name': 'Fazenda Santa Clara',
                'trade_name': 'Santa Clara Café',
                'supplier_type': 'company',
                'email': 'contato@santaclaracafe.com.br',
                'phone': '+5511999887766',
                'cnpj_cpf': '12.345.678/0001-90',
                'contact_person': 'Roberto Silva',
                'address': 'Fazenda Santa Clara, s/n',
                'city': 'Carmo de Minas',
                'state': 'MG',
                'postal_code': '37128-000',
                'country': 'BR',
                'payment_terms': 'À vista',
                'credit_rating': 'A',
            },
            {
                'code': 'FORN002',
                'name': 'Embalagens Premium Ltda',
                'trade_name': 'Premium Pack',
                'supplier_type': 'company',
                'email': 'vendas@premiumpack.com.br',
                'phone': '+5511988776655',
                'cnpj_cpf': '98.765.432/0001-10',
                'contact_person': 'Maria Fernanda',
                'address': 'Rua das Embalagens, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'postal_code': '01234-567',
                'country': 'BR',
                'payment_terms': '30 dias',
                'credit_rating': 'A',
            },
            {
                'code': 'FORN003',
                'name': 'Café Montanha Verde',
                'trade_name': 'Montanha Verde',
                'supplier_type': 'company',
                'email': 'comercial@montanhaverde.com.br',
                'phone': '+5535987654321',
                'cnpj_cpf': '55.444.333/0001-22',
                'contact_person': 'João Carlos',
                'address': 'Estrada da Montanha, km 15',
                'city': 'Poços de Caldas',
                'state': 'MG',
                'postal_code': '37701-000',
                'country': 'BR',
                'payment_terms': '15 dias',
                'credit_rating': 'B',
            },
        ]
        
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                code=sup_data['code'],
                defaults=sup_data
            )
            if created:
                self.created_data['suppliers'] += 1
                print(f"  ✅ Fornecedor criado: {supplier.name}")
    
    def create_customers(self):
        """Cria clientes."""
        print("\n👥 Criando clientes...")
        
        customers_data = [
            {
                'code': 'CLI001',
                'name': 'Cafeteria do Centro',
                'trade_name': 'Café Central',
                'customer_type': 'company',
                'email': 'pedidos@cafecentral.com.br',
                'phone': '+5511999123456',
                'cnpj_cpf': '11.222.333/0001-44',
                'address': 'Rua do Comércio, 456',
                'city': 'São Paulo',
                'state': 'SP',
                'postal_code': '01234-567',
                'credit_limit': Decimal('50000.00'),
                'payment_terms': '30 dias',
                'discount_percentage': Decimal('15.00'),
            },
            {
                'code': 'CLI002',
                'name': 'João dos Santos',
                'customer_type': 'individual',
                'email': 'joao.santos@email.com',
                'phone': '+5511988887777',
                'cnpj_cpf': '123.456.789-01',
                'address': 'Rua das Flores, 789',
                'city': 'São Paulo',
                'state': 'SP',
                'postal_code': '04567-890',
                'credit_limit': Decimal('5000.00'),
                'payment_terms': 'À vista',
                'discount_percentage': Decimal('5.00'),
            },
            {
                'code': 'CLI003',
                'name': 'Supermercado BomPreço',
                'trade_name': 'BomPreço',
                'customer_type': 'company',
                'email': 'compras@bompreco.com.br',
                'phone': '+5511977766655',
                'cnpj_cpf': '99.888.777/0001-66',
                'address': 'Avenida Principal, 1200',
                'city': 'São Paulo',
                'state': 'SP',
                'postal_code': '05678-901',
                'credit_limit': Decimal('100000.00'),
                'payment_terms': '45 dias',
                'discount_percentage': Decimal('20.00'),
            },
            {
                'code': 'CLI004',
                'name': 'Maria Silva',
                'customer_type': 'individual',
                'email': 'maria.silva@email.com',
                'phone': '+5511966655544',
                'cnpj_cpf': '987.654.321-09',
                'address': 'Rua das Palmeiras, 321',
                'city': 'São Paulo',
                'state': 'SP',
                'postal_code': '06789-012',
                'credit_limit': Decimal('3000.00'),
                'payment_terms': 'À vista',
                'discount_percentage': Decimal('0.00'),
            },
        ]
        
        for cust_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                code=cust_data['code'],
                defaults=cust_data
            )
            if created:
                self.created_data['customers'] += 1
                print(f"  ✅ Cliente criado: {customer.name}")
    
    def create_sales_orders(self):
        """Cria pedidos de venda."""
        print("\n🛒 Criando pedidos de venda...")
        
        customers = list(Customer.objects.all())
        products = list(Product.objects.all())
        
        # Data base para pedidos
        base_date = timezone.now().date()
        
        orders_data = [
            {
                'order_number': 'PV2025001',
                'customer': customers[0],  # Cafeteria do Centro
                'status': 'confirmed',
                'priority': 'normal',
                'delivery_date': base_date + timedelta(days=7),
                'payment_method': 'PIX',
                'payment_terms': '30 dias',
                'discount_percentage': Decimal('15.00'),
                'notes': 'Pedido regular da cafeteria',
                'items': [
                    {'product': products[0], 'quantity': 50, 'discount': 0},  # Café Gourmet 250g
                    {'product': products[1], 'quantity': 30, 'discount': 0},  # Café Premium 500g
                ]
            },
            {
                'order_number': 'PV2025002',
                'customer': customers[2],  # Supermercado BomPreço
                'status': 'confirmed',
                'priority': 'high',
                'delivery_date': base_date + timedelta(days=5),
                'payment_method': 'Boleto',
                'payment_terms': '45 dias',
                'discount_percentage': Decimal('20.00'),
                'notes': 'Pedido mensal do supermercado',
                'items': [
                    {'product': products[3], 'quantity': 100, 'discount': 0},  # Café Tradicional 250g
                    {'product': products[1], 'quantity': 50, 'discount': 0},   # Café Premium 500g
                    {'product': products[2], 'quantity': 20, 'discount': 0},   # Café Especial 1kg
                ]
            },
            {
                'order_number': 'PV2025003',
                'customer': customers[1],  # João dos Santos
                'status': 'pending',
                'priority': 'normal',
                'delivery_date': base_date + timedelta(days=3),
                'payment_method': 'Cartão de Crédito',
                'payment_terms': 'À vista',
                'discount_percentage': Decimal('5.00'),
                'notes': 'Cliente VIP',
                'items': [
                    {'product': products[4], 'quantity': 5, 'discount': 0},  # Café Orgânico 500g
                    {'product': products[0], 'quantity': 10, 'discount': 0}, # Café Gourmet 250g
                ]
            },
        ]
        
        for order_data in orders_data:
            items_data = order_data.pop('items')
            
            order, created = SalesOrder.objects.get_or_create(
                order_number=order_data['order_number'],
                defaults=order_data
            )
            
            if created:
                self.created_data['sales_orders'] += 1
                print(f"  ✅ Pedido criado: {order.order_number}")
                
                # Criar itens do pedido
                for item_data in items_data:
                    product = item_data['product']
                    SalesOrderItem.objects.create(
                        sales_order=order,
                        product=product,
                        quantity=item_data['quantity'],
                        unit_price=product.sale_price,
                        discount_percentage=item_data['discount']
                    )
                
                # Recalcular totais do pedido
                order.calculate_totals()
                order.save()
    
    def create_accounts_payable(self):
        """Cria contas a pagar."""
        print("\n💸 Criando contas a pagar...")
        
        suppliers = list(Supplier.objects.all())
        base_date = timezone.now().date()
        
        payables_data = [
            {
                'supplier': suppliers[0],
                'invoice_number': 'NF-001234',
                'invoice_date': base_date - timedelta(days=30),
                'due_date': base_date + timedelta(days=30),
                'original_amount': Decimal('15000.00'),
                'description': 'Compra de café verde premium - 800kg',
                'payment_method': 'transferencia_bancaria',
                'status': 'pending',
            },
            {
                'supplier': suppliers[1],
                'invoice_number': 'NF-005678',
                'invoice_date': base_date - timedelta(days=15),
                'due_date': base_date + timedelta(days=15),
                'original_amount': Decimal('3250.00'),
                'description': 'Embalagens vácuo - lote mensal',
                'payment_method': 'boleto',
                'status': 'pending',
            },
            {
                'supplier': suppliers[2],
                'invoice_number': 'NF-009876',
                'invoice_date': base_date - timedelta(days=45),
                'due_date': base_date - timedelta(days=15),
                'original_amount': Decimal('8750.00'),
                'description': 'Café verde robusta - 500kg',
                'payment_method': 'pix',
                'status': 'overdue',
            },
        ]
        
        for payable_data in payables_data:
            # Verificar se já existe
            existing = AccountsPayable.objects.filter(
                supplier=payable_data['supplier'],
                invoice_number=payable_data['invoice_number']
            ).first()
            
            if not existing:
                AccountsPayable.objects.create(**payable_data)
                self.created_data['accounts_payable'] += 1
                print(f"  ✅ Conta a pagar criada: {payable_data['invoice_number']}")
    
    def create_accounts_receivable(self):
        """Cria contas a receber."""
        print("\n💰 Criando contas a receber...")
        
        customers = list(Customer.objects.all())
        sales_orders = list(SalesOrder.objects.all())
        base_date = timezone.now().date()
        
        receivables_data = [
            {
                'customer': customers[0],
                'sales_order': sales_orders[0] if sales_orders else None,
                'invoice_number': 'FAT-001',
                'invoice_date': base_date - timedelta(days=10),
                'due_date': base_date + timedelta(days=20),
                'original_amount': Decimal('2200.00'),
                'description': 'Venda de café gourmet e premium',
                'payment_method': 'pix',
                'status': 'pending',
            },
            {
                'customer': customers[2],
                'sales_order': sales_orders[1] if len(sales_orders) > 1 else None,
                'invoice_number': 'FAT-002',
                'invoice_date': base_date - timedelta(days=5),
                'due_date': base_date + timedelta(days=40),
                'original_amount': Decimal('5850.00'),
                'description': 'Pedido mensal supermercado',
                'payment_method': 'boleto',
                'status': 'pending',
            },
            {
                'customer': customers[1],
                'invoice_number': 'FAT-003',
                'invoice_date': base_date - timedelta(days=20),
                'due_date': base_date - timedelta(days=5),
                'original_amount': Decimal('550.00'),
                'description': 'Venda café orgânico',
                'payment_method': 'cartao_credito',
                'status': 'overdue',
            },
        ]
        
        for receivable_data in receivables_data:
            # Verificar se já existe
            existing = AccountsReceivable.objects.filter(
                customer=receivable_data['customer'],
                invoice_number=receivable_data['invoice_number']
            ).first()
            
            if not existing:
                AccountsReceivable.objects.create(**receivable_data)
                self.created_data['accounts_receivable'] += 1
                print(f"  ✅ Conta a receber criada: {receivable_data['invoice_number']}")
    
    def create_recipes(self):
        """Cria receitas de produção."""
        print("\n📝 Criando receitas...")
        
        # Obter produtos e materiais
        products = list(Product.objects.all())
        materials = list(Material.objects.all())
        
        if not products or not materials:
            print("  ⚠️  Produtos ou materiais não encontrados. Pulando receitas.")
            return
        
        recipes_data = [
            {
                'code': 'REC001',
                'name': 'Receita Café Gourmet 250g',
                'description': 'Receita para produção do Café Gourmet 250g',
                'final_product': products[0],  # Café Gourmet 250g
                'batch_size': Decimal('100.00'),
                'items': [
                    {'material': materials[0], 'quantity': Decimal('30.00')},  # Café Verde Arábica
                    {'material': materials[2], 'quantity': Decimal('100.00')}, # Embalagem 250g
                ]
            },
            {
                'code': 'REC002',
                'name': 'Receita Café Premium 500g',
                'description': 'Receita para produção do Café Premium 500g',
                'final_product': products[1],  # Café Premium 500g
                'batch_size': Decimal('50.00'),
                'items': [
                    {'material': materials[0], 'quantity': Decimal('30.00')},  # Café Verde Arábica
                    {'material': materials[3], 'quantity': Decimal('50.00')},  # Embalagem 500g
                ]
            },
        ]
        
        for recipe_data in recipes_data:
            items_data = recipe_data.pop('items')
            
            recipe, created = Recipe.objects.get_or_create(
                code=recipe_data['code'],
                defaults=recipe_data
            )
            
            if created:
                self.created_data['recipes'] += 1
                print(f"  ✅ Receita criada: {recipe.name}")
                
                # Criar itens da receita
                for item_data in items_data:
                    RecipeItem.objects.create(
                        recipe=recipe,
                        material=item_data['material'],
                        quantity=item_data['quantity']
                    )
    
    def create_production_orders(self):
        """Cria ordens de produção."""
        print("\n🏭 Criando ordens de produção...")
        
        recipes = list(Recipe.objects.all())
        if not recipes:
            print("  ⚠️  Receitas não encontradas. Pulando ordens de produção.")
            return
        
        base_date = timezone.now().date()
        
        production_orders_data = [
            {
                'order_number': 'OP2025001',
                'recipe': recipes[0],
                'planned_quantity': Decimal('200.00'),
                'status': 'planned',
                'priority': 'normal',
                'planned_start_date': base_date + timedelta(days=1),
                'planned_end_date': base_date + timedelta(days=3),
                'notes': 'Produção para estoque',
            },
            {
                'order_number': 'OP2025002',
                'recipe': recipes[1] if len(recipes) > 1 else recipes[0],
                'planned_quantity': Decimal('100.00'),
                'status': 'in_progress',
                'priority': 'high',
                'planned_start_date': base_date,
                'planned_end_date': base_date + timedelta(days=2),
                'actual_start_date': base_date,
                'notes': 'Produção urgente para pedido',
            },
        ]
        
        for prod_data in production_orders_data:
            production_order, created = ProductionOrder.objects.get_or_create(
                order_number=prod_data['order_number'],
                defaults=prod_data
            )
            
            if created:
                self.created_data['production_orders'] += 1
                print(f"  ✅ Ordem de produção criada: {production_order.order_number}")
                
                # Criar itens da ordem de produção baseados na receita
                recipe = production_order.recipe
                planned_batches = production_order.planned_quantity / recipe.batch_size
                
                for recipe_item in recipe.recipe_items.all():
                    total_quantity = recipe_item.quantity * planned_batches
                    ProductionOrderItem.objects.create(
                        production_order=production_order,
                        material=recipe_item.material,
                        planned_quantity=total_quantity,
                        actual_quantity=total_quantity if prod_data['status'] == 'in_progress' else None
                    )
    
    def print_summary(self):
        """Imprime resumo dos dados criados."""
        print("\n" + "=" * 60)
        print("🎉 POPULATE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\n📊 RESUMO DOS DADOS CRIADOS:")
        print("-" * 40)
        
        for key, value in self.created_data.items():
            label = key.replace('_', ' ').title()
            print(f"  {label:.<30} {value:>5}")
        
        total = sum(self.created_data.values())
        print("-" * 40)
        print(f"  {'TOTAL':.<30} {total:>5}")
        
        print("\n🚀 O sistema está pronto para demonstração!")
        print("\n💡 CREDENCIAIS DE ACESSO:")
        print("  Usuário: admin")
        print("  Senha: demo123")
        
        print("\n🌐 ACESSE O SISTEMA:")
        print("  http://127.0.0.1:8000/admin/")
        print("  http://127.0.0.1:8000/dashboard/")


if __name__ == "__main__":
    populator = DemoDataPopulator()
    populator.run()
