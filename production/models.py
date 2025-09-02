"""
Production models for coffee_factory project.
Models for production orders, recipes, and manufacturing processes.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import BaseModel, AuditModel


class Recipe(AuditModel):
    """Recipe model defining how to make a product."""
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('active', 'Ativo'),
        ('testing', 'Em Teste'),
        ('inactive', 'Inativo'),
        ('archived', 'Arquivado'),
    ]
    
    COMPLEXITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único da receita"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nome da receita"
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text="Produto que será produzido"
    )
    version = models.CharField(
        max_length=10,
        default='1.0',
        help_text="Versão da receita"
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição do processo de produção"
    )
    yield_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Quantidade produzida por lote"
    )
    estimated_time_minutes = models.PositiveIntegerField(
        help_text="Tempo estimado de produção em minutos"
    )
    complexity = models.CharField(
        max_length=10,
        choices=COMPLEXITY_CHOICES,
        default='medium',
        help_text="Complexidade da receita"
    )
    instructions = models.TextField(
        blank=True,
        help_text="Instruções passo a passo para o preparo"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Status da receita"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações sobre a receita"
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['code']
        unique_together = ['product', 'version']

    def __str__(self):
        return f"{self.code} - {self.name} v{self.version}"

    @property
    def total_material_cost(self):
        """Calculate total cost of materials for this recipe."""
        return sum(
            item.quantity * item.material.cost_per_unit
            for item in self.recipe_items.all()
        )

    @property
    def cost_per_unit(self):
        """Calculate cost per unit produced."""
        if self.yield_quantity > 0:
            return self.total_material_cost / self.yield_quantity
        return 0
    
    @property
    def instructions_list(self):
        """Return instructions as a list of steps."""
        if self.instructions:
            return [step.strip() for step in self.instructions.split('\n') if step.strip()]
        return []


class RecipeItem(BaseModel):
    """Recipe item model for materials needed in a recipe."""
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_items',
        help_text="Receita"
    )
    material = models.ForeignKey(
        'inventory.Material',
        on_delete=models.CASCADE,
        related_name='recipe_items',
        help_text="Material necessário"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Quantidade necessária do material"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordem de utilização na receita"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações sobre o uso do material"
    )

    class Meta:
        verbose_name = 'Recipe Item'
        verbose_name_plural = 'Recipe Items'
        ordering = ['order', 'material__name']
        unique_together = ['recipe', 'material']

    def __str__(self):
        return f"{self.recipe.name} - {self.material.name} ({self.quantity})"

    @property
    def total_cost(self):
        """Calculate total cost for this recipe item."""
        return self.quantity * self.material.cost_per_unit


class ProductionOrder(AuditModel):
    """Production order model for manufacturing requests."""
    
    STATUS_CHOICES = [
        ('planned', 'Planejado'),
        ('approved', 'Aprovado'),
        ('in_progress', 'Em Produção'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
        ('on_hold', 'Pausado'),
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
        help_text="Número único da ordem de produção"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.PROTECT,
        related_name='production_orders',
        help_text="Receita a ser utilizada"
    )
    planned_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Quantidade planejada para produção"
    )
    produced_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Quantidade efetivamente produzida"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        help_text="Status da ordem de produção"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        help_text="Prioridade da ordem"
    )
    
    # Dates
    planned_start_date = models.DateTimeField(
        help_text="Data planejada para início"
    )
    planned_end_date = models.DateTimeField(
        help_text="Data planejada para conclusão"
    )
    actual_start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data real de início"
    )
    actual_end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data real de conclusão"
    )
    
    # Responsible
    supervisor = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.PROTECT,
        related_name='supervised_orders',
        help_text="Responsável pela produção"
    )
    
    # Costs
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custo estimado"
    )
    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custo real"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )
    
    # Related orders
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='production_orders',
        help_text="Pedido de venda relacionado (opcional)"
    )

    class Meta:
        verbose_name = 'Production Order'
        verbose_name_plural = 'Production Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"OP {self.order_number} - {self.recipe.product.name}"

    @property
    def completion_percentage(self):
        """Calculate completion percentage."""
        if self.planned_quantity > 0:
            return min((self.produced_quantity / self.planned_quantity) * 100, 100)
        return 0

    @property
    def is_overdue(self):
        """Check if production order is overdue."""
        from django.utils import timezone
        if self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.planned_end_date
        return False

    @property
    def materials_needed(self):
        """Get list of materials needed for this production order."""
        multiplier = self.planned_quantity / self.recipe.yield_quantity
        return [
            {
                'material': item.material,
                'quantity_needed': item.quantity * multiplier,
                'available_stock': item.material.current_stock,
                'shortage': max(0, (item.quantity * multiplier) - item.material.current_stock)
            }
            for item in self.recipe.recipe_items.all()
        ]

    def can_start_production(self):
        """Check if all materials are available to start production."""
        return all(
            material['shortage'] == 0
            for material in self.materials_needed
        )

    def reserve_materials(self):
        """Reserve materials for production (create negative stock movements)."""
        if not self.can_start_production():
            raise ValueError("Insufficient materials to start production")
        
        from inventory.models import StockMovement
        
        multiplier = self.planned_quantity / self.recipe.yield_quantity
        
        for item in self.recipe.recipe_items.all():
            quantity_needed = item.quantity * multiplier
            
            StockMovement.objects.create(
                material=item.material,
                movement_type='out',
                reason='production',
                quantity=-quantity_needed,
                unit_cost=item.material.cost_per_unit,
                production_order=self,
                document_number=self.order_number,
                notes=f"Reserva para OP {self.order_number}",
                created_by=self.created_by
            )

    def complete_production(self, actual_quantity=None):
        """Complete production and add finished goods to inventory."""
        if actual_quantity is None:
            actual_quantity = self.planned_quantity
        
        self.produced_quantity = actual_quantity
        self.status = 'completed'
        
        from django.utils import timezone
        if not self.actual_end_date:
            self.actual_end_date = timezone.now()
        
        # Add finished product to inventory
        from inventory.models import StockMovement
        
        StockMovement.objects.create(
            product=self.recipe.product,
            movement_type='in',
            reason='production',
            quantity=actual_quantity,
            unit_cost=self.recipe.cost_per_unit,
            production_order=self,
            document_number=self.order_number,
            notes=f"Produção concluída - OP {self.order_number}",
            created_by=self.updated_by
        )
        
        self.save()


class ProductionOrderItem(BaseModel):
    """Production order item for tracking material consumption."""
    
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='production_items',
        help_text="Ordem de produção"
    )
    material = models.ForeignKey(
        'inventory.Material',
        on_delete=models.CASCADE,
        related_name='production_items',
        help_text="Material consumido"
    )
    planned_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Quantidade planejada"
    )
    consumed_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Quantidade efetivamente consumida"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Custo unitário no momento da produção"
    )

    class Meta:
        verbose_name = 'Production Order Item'
        verbose_name_plural = 'Production Order Items'
        ordering = ['material__name']
        unique_together = ['production_order', 'material']

    def __str__(self):
        return f"{self.production_order.order_number} - {self.material.name}"

    @property
    def total_planned_cost(self):
        """Calculate total planned cost."""
        return self.planned_quantity * self.unit_cost

    @property
    def total_actual_cost(self):
        """Calculate total actual cost."""
        return self.consumed_quantity * self.unit_cost

    @property
    def variance_quantity(self):
        """Calculate quantity variance."""
        return self.consumed_quantity - self.planned_quantity

    @property
    def variance_cost(self):
        """Calculate cost variance."""
        return self.total_actual_cost - self.total_planned_cost
