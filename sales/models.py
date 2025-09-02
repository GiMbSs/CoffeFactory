"""
Sales models for coffee_factory project.
Models for customers, sales orders, and sales management.
"""

from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
from core.models import BaseModel, AuditModel


class Customer(BaseModel):
    """Customer model for sales management."""
    
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Pessoa Física'),
        ('company', 'Pessoa Jurídica'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('blocked', 'Bloqueado'),
    ]
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código único do cliente"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nome/Razão social do cliente"
    )
    trade_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nome fantasia"
    )
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='individual',
        help_text="Tipo de cliente"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Status do cliente"
    )
    
    # Document numbers
    cnpj_cpf = models.CharField(
        max_length=18,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message="CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX ou CPF no formato XXX.XXX.XXX-XX"
            )
        ],
        help_text="CNPJ ou CPF"
    )
    state_registration = models.CharField(
        max_length=20,
        blank=True,
        help_text="Inscrição estadual"
    )
    
    # Contact information
    email = models.EmailField(
        blank=True,
        help_text="Email principal"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Telefone deve estar no formato '+999999999'. Até 15 dígitos."
            )
        ],
        help_text="Telefone principal"
    )
    mobile = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Celular deve estar no formato '+999999999'. Até 15 dígitos."
            )
        ],
        help_text="Celular"
    )
    
    # Address
    address = models.CharField(
        max_length=200,
        blank=True,
        help_text="Endereço"
    )
    address_number = models.CharField(
        max_length=10,
        blank=True,
        help_text="Número"
    )
    address_complement = models.CharField(
        max_length=100,
        blank=True,
        help_text="Complemento"
    )
    neighborhood = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bairro"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cidade"
    )
    state = models.CharField(
        max_length=2,
        blank=True,
        help_text="Estado (UF)"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-?\d{3}$',
                message="CEP deve estar no formato XXXXX-XXX"
            )
        ],
        help_text="CEP"
    )
    country = models.CharField(
        max_length=50,
        default='Brasil',
        help_text="País"
    )
    
    # Sales information
    sales_representative = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        limit_choices_to={'department': 'sales'},
        help_text="Representante de vendas"
    )
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Limite de crédito"
    )
    payment_terms = models.CharField(
        max_length=100,
        blank=True,
        help_text="Condições de pagamento"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0')), MinValueValidator(Decimal('100'))],
        help_text="Desconto padrão (%)"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']

    def __str__(self):
        display_name = self.trade_name if self.trade_name else self.name
        return f"{self.code} - {display_name}"

    @property
    def full_address(self):
        """Get formatted full address."""
        address_parts = []
        
        if self.address:
            address_line = self.address
            if self.address_number:
                address_line += f", {self.address_number}"
            if self.address_complement:
                address_line += f" - {self.address_complement}"
            address_parts.append(address_line)
        
        if self.neighborhood:
            address_parts.append(self.neighborhood)
        
        if self.city and self.state:
            address_parts.append(f"{self.city}/{self.state}")
        elif self.city:
            address_parts.append(self.city)
        
        if self.postal_code:
            address_parts.append(f"CEP: {self.postal_code}")
        
        return " - ".join(address_parts) if address_parts else ""

    @property
    def current_debt(self):
        """Calculate current debt from pending sales orders."""
        return self.sales_orders.filter(
            status__in=['confirmed', 'partially_paid']
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0

    @property
    def available_credit(self):
        """Calculate available credit limit."""
        if self.credit_limit:
            return max(0, self.credit_limit - self.current_debt)
        return 0

    def get_display_name(self):
        """Get the display name (trade name or name)."""
        return self.trade_name if self.trade_name else self.name


class SalesOrder(AuditModel):
    """Sales order model for managing customer orders."""
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('confirmed', 'Confirmado'),
        ('in_production', 'Em Produção'),
        ('ready', 'Pronto'),
        ('delivered', 'Entregue'),
        ('partially_paid', 'Parcialmente Pago'),
        ('paid', 'Pago'),
        ('cancelled', 'Cancelado'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número único do pedido de venda"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales_orders',
        help_text="Cliente"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Status do pedido"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        help_text="Prioridade do pedido"
    )
    
    # Dates
    order_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Data do pedido"
    )
    delivery_date = models.DateField(
        help_text="Data de entrega prometida"
    )
    actual_delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data real de entrega"
    )
    
    # Sales information
    sales_representative = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.PROTECT,
        related_name='sales_orders',
        limit_choices_to={'department': 'sales'},
        help_text="Representante de vendas"
    )
    
    # Financial information
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Subtotal (sem desconto e impostos)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0')), MinValueValidator(Decimal('100'))],
        help_text="Desconto (%)"
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Valor do desconto"
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Impostos (%)"
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Valor dos impostos"
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Custo de envio"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Valor total do pedido"
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor já pago"
    )
    
    # Payment information
    payment_terms = models.CharField(
        max_length=100,
        blank=True,
        help_text="Condições de pagamento"
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Forma de pagamento"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )
    internal_notes = models.TextField(
        blank=True,
        help_text="Observações internas"
    )

    class Meta:
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'
        ordering = ['-order_date']

    def __str__(self):
        return f"PV {self.order_number} - {self.customer.get_display_name()}"

    @property
    def pending_amount(self):
        """Calculate pending payment amount."""
        return max(0, self.total_amount - self.paid_amount)

    @property
    def is_overdue(self):
        """Check if order is overdue for delivery."""
        from django.utils import timezone
        if self.status not in ['delivered', 'paid', 'cancelled']:
            return timezone.now().date() > self.delivery_date
        return False

    @property
    def profit_margin(self):
        """Calculate profit margin."""
        total_cost = sum(item.total_cost for item in self.order_items.all())
        if total_cost > 0:
            profit = self.total_amount - total_cost
            return (profit / self.total_amount) * 100
        return 0

    def calculate_totals(self):
        """Calculate and update order totals."""
        # Calculate subtotal from items
        self.subtotal = sum(item.total_price for item in self.order_items.all())
        
        # Calculate discount
        if self.discount_percentage > 0:
            self.discount_amount = (self.subtotal * self.discount_percentage) / 100
        
        # Calculate net amount after discount
        net_amount = self.subtotal - self.discount_amount
        
        # Calculate tax
        if self.tax_percentage > 0:
            self.tax_amount = (net_amount * self.tax_percentage) / 100
        
        # Calculate total
        self.total_amount = net_amount + self.tax_amount + self.shipping_cost
        
        self.save()

    def can_be_produced(self):
        """Check if all items can be produced (stock availability)."""
        for item in self.order_items.all():
            if item.product.current_stock < item.quantity:
                return False
        return True

    def create_production_orders(self):
        """Create production orders for items that need manufacturing."""
        from production.models import ProductionOrder
        production_orders = []
        
        for item in self.order_items.all():
            if item.quantity > item.product.current_stock:
                # Check if product has recipes
                active_recipe = item.product.recipes.filter(status='active').first()
                if active_recipe:
                    # Create production order
                    po = ProductionOrder.objects.create(
                        order_number=f"OP-{self.order_number}-{item.product.code}",
                        recipe=active_recipe,
                        planned_quantity=item.quantity,
                        supervisor=self.sales_representative,  # Or assign to production supervisor
                        planned_start_date=timezone.now(),
                        planned_end_date=self.delivery_date,
                        sales_order=self,
                        notes=f"Produção para pedido {self.order_number}",
                        created_by=self.created_by
                    )
                    production_orders.append(po)
        
        return production_orders


class SalesOrderItem(BaseModel):
    """Sales order item model for order line items."""
    
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='order_items',
        help_text="Pedido de venda"
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='sales_order_items',
        help_text="Produto"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Quantidade"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Preço unitário"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0')), MinValueValidator(Decimal('100'))],
        help_text="Desconto item (%)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Valor do desconto do item"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Preço total do item"
    )
    delivered_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Quantidade entregue"
    )

    class Meta:
        verbose_name = 'Sales Order Item'
        verbose_name_plural = 'Sales Order Items'
        ordering = ['product__name']
        unique_together = ['sales_order', 'product']

    def __str__(self):
        return f"{self.sales_order.order_number} - {self.product.name}"

    @property
    def total_cost(self):
        """Calculate total cost for this item."""
        return self.quantity * self.product.cost_per_unit

    @property
    def profit_amount(self):
        """Calculate profit amount for this item."""
        return self.total_price - self.total_cost

    @property
    def pending_quantity(self):
        """Calculate pending delivery quantity."""
        return max(0, self.quantity - self.delivered_quantity)

    def save(self, *args, **kwargs):
        """Override save to calculate totals."""
        # Calculate discount amount
        if self.discount_percentage > 0:
            self.discount_amount = (self.quantity * self.unit_price * self.discount_percentage) / 100
        
        # Calculate total price
        gross_amount = self.quantity * self.unit_price
        self.total_price = gross_amount - self.discount_amount
        
        super().save(*args, **kwargs)
        
        # Update order totals
        if hasattr(self, 'sales_order'):
            self.sales_order.calculate_totals()
