"""
Script de populate simplificado para executar via Django shell.
Execute com: python manage.py shell
exec(open('scripts/populate_simple.py').read())
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from accounts.models import Employee
from inventory.models import Category, UnitOfMeasure, Material, Product
from suppliers.models import Supplier
from sales.models import Customer, SalesOrder, SalesOrderItem
from financial.models import AccountsPayable, AccountsReceivable

User = get_user_model()

print("🚀 Iniciando populate de dados de demonstração...")
print("=" * 60)

# 1. Criar usuário admin se não existir
print("👥 Criando usuário admin...")
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@coffeefactory.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('demo123')
    admin_user.save()
    print("  ✅ Usuário admin criado")
else:
    print("  ℹ️  Usuário admin já existe")

# 2. Criar funcionários
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
]

for emp_data in employees_data:
    employee, created = Employee.objects.get_or_create(
        code=emp_data['code'],
        defaults=emp_data
    )
    if created:
        print(f"  ✅ Funcionário criado: {employee.first_name} {employee.last_name}")

# 3. Criar categorias
print("\n📁 Criando categorias...")
categories_data = [
    {'name': 'Café Torrado', 'description': 'Cafés torrados em diferentes níveis'},
    {'name': 'Café Verde', 'description': 'Grãos de café verde para torrefação'},
    {'name': 'Embalagens', 'description': 'Materiais de embalagem'},
    {'name': 'Especiais', 'description': 'Cafés especiais e gourmet'},
]

for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults=cat_data
    )
    if created:
        print(f"  ✅ Categoria criada: {category.name}")

# 4. Criar unidades de medida
print("\n📏 Criando unidades de medida...")
units_data = [
    {'name': 'Quilograma', 'symbol': 'kg', 'description': 'Quilograma'},
    {'name': 'Grama', 'symbol': 'g', 'description': 'Grama'},
    {'name': 'Unidade', 'symbol': 'un', 'description': 'Unidade'},
    {'name': 'Pacote', 'symbol': 'pct', 'description': 'Pacote'},
]

for unit_data in units_data:
    unit, created = UnitOfMeasure.objects.get_or_create(
        symbol=unit_data['symbol'],
        defaults=unit_data
    )
    if created:
        print(f"  ✅ Unidade criada: {unit.name} ({unit.symbol})")

# 5. Criar produtos
print("\n☕ Criando produtos...")
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
        print(f"  ✅ Produto criado: {product.name}")

# 6. Criar fornecedores
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
]

for sup_data in suppliers_data:
    supplier, created = Supplier.objects.get_or_create(
        code=sup_data['code'],
        defaults=sup_data
    )
    if created:
        print(f"  ✅ Fornecedor criado: {supplier.name}")

# 7. Criar clientes
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
]

for cust_data in customers_data:
    customer, created = Customer.objects.get_or_create(
        code=cust_data['code'],
        defaults=cust_data
    )
    if created:
        print(f"  ✅ Cliente criado: {customer.name}")

# 8. Criar contas a pagar
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
        'supplier': suppliers[1] if len(suppliers) > 1 else suppliers[0],
        'invoice_number': 'NF-005678',
        'invoice_date': base_date - timedelta(days=15),
        'due_date': base_date + timedelta(days=15),
        'original_amount': Decimal('3250.00'),
        'description': 'Embalagens vácuo - lote mensal',
        'payment_method': 'boleto',
        'status': 'pending',
    },
]

for payable_data in payables_data:
    existing = AccountsPayable.objects.filter(
        supplier=payable_data['supplier'],
        invoice_number=payable_data['invoice_number']
    ).first()
    
    if not existing:
        AccountsPayable.objects.create(**payable_data)
        print(f"  ✅ Conta a pagar criada: {payable_data['invoice_number']}")

# 9. Criar contas a receber
print("\n💰 Criando contas a receber...")
customers = list(Customer.objects.all())

receivables_data = [
    {
        'customer': customers[0],
        'invoice_number': 'FAT-001',
        'invoice_date': base_date - timedelta(days=10),
        'due_date': base_date + timedelta(days=20),
        'original_amount': Decimal('2200.00'),
        'description': 'Venda de café gourmet e premium',
        'payment_method': 'pix',
        'status': 'pending',
    },
    {
        'customer': customers[2] if len(customers) > 2 else customers[0],
        'invoice_number': 'FAT-002',
        'invoice_date': base_date - timedelta(days=5),
        'due_date': base_date + timedelta(days=40),
        'original_amount': Decimal('5850.00'),
        'description': 'Pedido mensal supermercado',
        'payment_method': 'boleto',
        'status': 'pending',
    },
]

for receivable_data in receivables_data:
    existing = AccountsReceivable.objects.filter(
        customer=receivable_data['customer'],
        invoice_number=receivable_data['invoice_number']
    ).first()
    
    if not existing:
        AccountsReceivable.objects.create(**receivable_data)
        print(f"  ✅ Conta a receber criada: {receivable_data['invoice_number']}")

print("\n" + "=" * 60)
print("🎉 POPULATE CONCLUÍDO COM SUCESSO!")
print("=" * 60)

print("\n💡 CREDENCIAIS DE ACESSO:")
print("  Usuário: admin")
print("  Senha: demo123")

print("\n🌐 ACESSE O SISTEMA:")
print("  http://127.0.0.1:8000/admin/")
print("  http://127.0.0.1:8000/dashboard/")
