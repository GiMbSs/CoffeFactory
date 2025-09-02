"""
Inventory models for coffee_factory project.
Models for materials, products, and stock management.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import BaseModel, AuditModel


class Category(BaseModel):
    """Category model for organizing materials and products."""
    
    CATEGORY_TYPE_CHOICES = [
        ('material', 'Material/Insumo'),
        ('product', 'Produto Acabado'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Nome da categoria"
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição da categoria"
    )
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPE_CHOICES,
        help_text="Tipo da categoria"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Categoria pai (para subcategorias)"
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ['name', 'category_type']

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class UnitOfMeasure(BaseModel):
    """Unit of measure for materials and products."""
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nome da unidade (ex: kg, litro, unidade)"
    )
    abbreviation = models.CharField(
        max_length=10,
        unique=True,
        help_text="Abreviação da unidade (ex: kg, L, un)"
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição da unidade"
    )

    class Meta:
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Material(AuditModel):
    """Material/Raw material model for production inputs."""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('discontinued', 'Descontinuado'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único do material"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nome do material"
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição detalhada do material"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='materials',
        limit_choices_to={'category_type': 'material'},
        help_text="Categoria do material"
    )
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='materials',
        help_text="Unidade de medida"
    )
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Custo por unidade em reais"
    )
    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Estoque mínimo"
    )
    maximum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Estoque máximo (opcional)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Status do material"
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
        help_text="Fornecedor principal"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def current_stock(self):
        """Get current stock quantity."""
        return self.stock_movements.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def stock_value(self):
        """Get current stock value."""
        return self.current_stock * self.cost_per_unit

    def is_low_stock(self):
        """Check if material is below minimum stock."""
        return self.current_stock <= self.minimum_stock


class Product(AuditModel):
    """Finished product model."""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('discontinued', 'Descontinuado'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único do produto"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nome do produto"
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição detalhada do produto"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        limit_choices_to={'category_type': 'product'},
        help_text="Categoria do produto"
    )
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='products',
        help_text="Unidade de medida"
    )
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Custo de produção por unidade"
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Preço de venda por unidade"
    )
    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Estoque mínimo"
    )
    maximum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Estoque máximo (opcional)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Status do produto"
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Peso em kg (opcional)"
    )
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        help_text="Dimensões (ex: 10x15x20 cm)"
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        help_text="Código de barras"
    )
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        help_text="Imagem do produto"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def current_stock(self):
        """Get current stock quantity."""
        return self.stock_movements.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def stock_value(self):
        """Get current stock value at cost."""
        return self.current_stock * self.cost_per_unit

    @property
    def stock_sale_value(self):
        """Get current stock value at sale price."""
        return self.current_stock * self.sale_price

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost_per_unit > 0:
            return ((self.sale_price - self.cost_per_unit) / self.cost_per_unit) * 100
        return 0

    def is_low_stock(self):
        """Check if product is below minimum stock."""
        return self.current_stock <= self.minimum_stock


class StockMovement(AuditModel):
    """Stock movement model for tracking inventory changes."""
    
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Entrada'),
        ('out', 'Saída'),
        ('adjustment', 'Ajuste'),
        ('transfer', 'Transferência'),
    ]
    
    REASON_CHOICES = [
        ('purchase', 'Compra'),
        ('production', 'Produção'),
        ('sale', 'Venda'),
        ('loss', 'Perda'),
        ('damaged', 'Danificado'),
        ('expired', 'Vencido'),
        ('adjustment', 'Ajuste de Inventário'),
        ('return', 'Devolução'),
        ('transfer', 'Transferência'),
        ('initial', 'Estoque Inicial'),
    ]
    
    # Generic relation to allow both Material and Product
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stock_movements',
        help_text="Material relacionado"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stock_movements',
        help_text="Produto relacionado"
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        help_text="Tipo de movimentação"
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        help_text="Motivo da movimentação"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="Quantidade (positiva para entrada, negativa para saída)"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custo unitário na movimentação"
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custo total da movimentação"
    )
    document_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Número do documento (NF, OP, etc.)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )
    
    # Reference to related transactions
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stock_movements',
        help_text="Ordem de produção relacionada"
    )
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stock_movements',
        help_text="Pedido de venda relacionado"
    )

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-created_at']

    def __str__(self):
        item = self.material or self.product
        item_type = "Material" if self.material else "Product"
        return f"{item_type}: {item} - {self.get_movement_type_display()} ({self.quantity})"

    def clean(self):
        """Validate that either material or product is set, but not both."""
        from django.core.exceptions import ValidationError
        
        if not self.material and not self.product:
            raise ValidationError("Deve ser especificado um material ou produto.")
        
        if self.material and self.product:
            raise ValidationError("Não é possível especificar material e produto ao mesmo tempo.")
        
        # Set sign based on movement type
        if self.movement_type == 'out' and self.quantity > 0:
            self.quantity = -self.quantity
        elif self.movement_type == 'in' and self.quantity < 0:
            self.quantity = -self.quantity

    def save(self, *args, **kwargs):
        """Override save to calculate total cost and validate."""
        self.clean()
        
        # Calculate total cost if unit cost is provided
        if self.unit_cost and not self.total_cost:
            self.total_cost = abs(self.quantity) * self.unit_cost
        
        super().save(*args, **kwargs)

    @property
    def item(self):
        """Get the related item (material or product)."""
        return self.material or self.product

    @property
    def item_type(self):
        """Get the type of item."""
        return "material" if self.material else "product"
