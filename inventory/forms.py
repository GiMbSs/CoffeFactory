"""
Forms for inventory app.
Forms for materials, products, stock movements, and inventory management.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re

from core.forms import BaseModelForm
from .models import Category, Material, Product, StockMovement, UnitOfMeasure


class CategoryForm(BaseModelForm):
    """Form for Category model."""
    
    class Meta:
        model = Category
        fields = [
            'name', 'description', 'category_type', 'parent', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome da categoria'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descrição da categoria'
            }),
            'category_type': forms.Select(),
            'parent': forms.Select(attrs={
                'placeholder': 'Categoria pai (opcional)'
            }),
            'is_active': forms.CheckboxInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter parent categories to prevent circular references
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(
                pk=self.instance.pk
            ).exclude(
                parent=self.instance
            )
    
    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        
        # Prevent self-reference
        if parent == self.instance:
            raise ValidationError('Uma categoria não pode ser pai de si mesma.')
        
        # Prevent circular references
        if parent and self.instance.pk:
            current = parent
            while current:
                if current == self.instance:
                    raise ValidationError('Referência circular detectada na hierarquia de categorias.')
                current = current.parent
        
        return cleaned_data


class MaterialForm(forms.ModelForm):
    """Form for Material model."""
    
    class Meta:
        model = Material
        fields = [
            'name', 'code', 'description', 'category', 'supplier', 
            'unit_of_measure', 'cost_per_unit', 'minimum_stock', 
            'maximum_stock', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome do material'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Código do material'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Descrição detalhada'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit_of_measure': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cost_per_unit': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'minimum_stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'maximum_stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Observações sobre o material'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories to only material categories
        self.fields['category'].queryset = Category.objects.filter(
            category_type='material', is_active=True
        )
        # Filter active suppliers
        from suppliers.models import Supplier
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        # Filter active units of measure
        self.fields['unit_of_measure'].queryset = UnitOfMeasure.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        minimum_stock = cleaned_data.get('minimum_stock')
        maximum_stock = cleaned_data.get('maximum_stock')
        
        # Validate stock levels
        if minimum_stock and maximum_stock:
            if minimum_stock >= maximum_stock:
                raise ValidationError({
                    'minimum_stock': 'O estoque mínimo deve ser menor que o estoque máximo.'
                })
        
        return cleaned_data


class ProductForm(forms.ModelForm):
    """Form for Product model."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'description', 'category', 'sale_price',
            'minimum_stock', 'maximum_stock', 'weight', 'dimensions',
            'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome do produto'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Código do produto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Descrição detalhada'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'minimum_stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'maximum_stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.001',
                'min': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dimensões (LxAxP)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Observações sobre o produto'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories to only product categories
        self.fields['category'].queryset = Category.objects.filter(
            category_type='product', is_active=True
        )
    
    def clean(self):
        cleaned_data = super().clean()
        minimum_stock = cleaned_data.get('minimum_stock')
        maximum_stock = cleaned_data.get('maximum_stock')
        
        # Validate stock levels
        if minimum_stock and maximum_stock:
            if minimum_stock >= maximum_stock:
                raise ValidationError({
                    'minimum_stock': 'O estoque mínimo deve ser menor que o estoque máximo.'
                })
        
        return cleaned_data


class StockMovementForm(forms.ModelForm):
    """Form for StockMovement model."""
    
    class Meta:
        model = StockMovement
        fields = [
            'material', 'product', 'movement_type', 'quantity', 
            'reason', 'document_number', 'notes'
        ]
        widgets = {
            'material': forms.Select(attrs={
                'class': 'form-select'
            }),
            'product': forms.Select(attrs={
                'class': 'form-select'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01'
            }),
            'reason': forms.Select(attrs={
                'class': 'form-select'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Número do documento de referência'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Observações adicionais'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active materials and products
        self.fields['material'].queryset = Material.objects.filter(is_active=True)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Make material and product optional (one of them is required)
        self.fields['material'].required = False
        self.fields['product'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        material = cleaned_data.get('material')
        product = cleaned_data.get('product')
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')
        
        # Ensure either material or product is selected
        if not material and not product:
            raise ValidationError('Selecione um material ou produto.')
        
        # Ensure only one is selected
        if material and product:
            raise ValidationError('Selecione apenas um material ou produto, não ambos.')
        
        # Validate exit quantity against current stock
        if movement_type == 'exit' and quantity:
            current_stock = 0
            if material:
                current_stock = material.current_stock
            elif product:
                current_stock = product.current_stock
            
            if quantity > current_stock:
                raise ValidationError({
                    'quantity': f'Quantidade insuficiente em estoque. Disponível: {current_stock}'
                })
        
        return cleaned_data


class MaterialFilterForm(forms.Form):
    """Form for filtering materials."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por nome, código ou descrição...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(category_type='material', is_active=True),
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    supplier = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label='Todos os fornecedores',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('available', 'Disponível'),
        ('low_stock', 'Estoque baixo'),
        ('out_of_stock', 'Sem estoque'),
        ('inactive', 'Inativo'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    low_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    ORDERING_CHOICES = [
        ('name', 'Nome (A-Z)'),
        ('-name', 'Nome (Z-A)'),
        ('code', 'Código (A-Z)'),
        ('-code', 'Código (Z-A)'),
        ('current_stock', 'Estoque (menor)'),
        ('-current_stock', 'Estoque (maior)'),
        ('cost_per_unit', 'Preço (menor)'),
        ('-cost_per_unit', 'Preço (maior)'),
        ('created_at', 'Criação (antigo)'),
        ('-created_at', 'Criação (recente)'),
    ]
    
    ordering = forms.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        initial='name',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set supplier queryset
        from suppliers.models import Supplier
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)


class CategoryFilterForm(forms.Form):
    """Form for filtering categories."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por nome ou descrição...'
        })
    )
    
    CATEGORY_TYPE_CHOICES = [
        ('', 'Todos os tipos'),
        ('material', 'Material'),
        ('product', 'Produto'),
    ]
    
    category_type = forms.ChoiceField(
        choices=CATEGORY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    IS_ACTIVE_CHOICES = [
        ('', 'Todos'),
        ('true', 'Ativo'),
        ('false', 'Inativo'),
    ]
    
    is_active = forms.ChoiceField(
        choices=IS_ACTIVE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ORDERING_CHOICES = [
        ('name', 'Nome (A-Z)'),
        ('-name', 'Nome (Z-A)'),
        ('category_type', 'Tipo (A-Z)'),
        ('-category_type', 'Tipo (Z-A)'),
        ('created_at', 'Criação (antigo)'),
        ('-created_at', 'Criação (recente)'),
    ]
    
    ordering = forms.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        initial='name',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class StockAdjustmentForm(forms.Form):
    """Form for manual stock adjustments."""
    
    ADJUSTMENT_TYPE_CHOICES = [
        ('increase', 'Aumentar Estoque'),
        ('decrease', 'Diminuir Estoque'),
        ('set', 'Definir Quantidade'),
    ]
    
    material = forms.ModelChoiceField(
        queryset=Material.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    adjustment_type = forms.ChoiceField(
        choices=ADJUSTMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=0.001,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.001',
            'min': '0.001'
        })
    )
    reason = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Motivo do ajuste'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        material = cleaned_data.get('material')
        adjustment_type = cleaned_data.get('adjustment_type')
        quantity = cleaned_data.get('quantity')
        
        if material and adjustment_type == 'decrease':
            current_stock = getattr(material, 'current_stock', 0)
            if quantity > current_stock:
                raise ValidationError(
                    f'Não é possível diminuir {quantity} unidades. '
                    f'Estoque atual: {current_stock}'
                )
        
        return cleaned_data


class InventoryReportForm(forms.Form):
    """Form for inventory reports."""
    
    REPORT_TYPE_CHOICES = [
        ('stock_levels', 'Níveis de Estoque'),
        ('low_stock', 'Estoque Baixo'),
        ('stock_movements', 'Movimentações de Estoque'),
        ('abc_analysis', 'Análise ABC'),
        ('valuation', 'Valorização do Estoque'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    include_inactive = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError('A data final deve ser posterior à data inicial.')
        
        return cleaned_data


class MaterialTransferForm(forms.Form):
    """Form for transferring materials between locations."""
    
    material = forms.ModelChoiceField(
        queryset=Material.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    from_location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Localização de origem'
        })
    )
    to_location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Localização de destino'
        })
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=0.001,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.001',
            'min': '0.001'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 2,
            'placeholder': 'Observações sobre a transferência'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        from_location = cleaned_data.get('from_location')
        to_location = cleaned_data.get('to_location')
        
        if from_location and to_location:
            if from_location.lower() == to_location.lower():
                raise ValidationError('As localizações de origem e destino devem ser diferentes.')
        
        return cleaned_data
