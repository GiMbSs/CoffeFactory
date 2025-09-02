"""
Forms for production app.
Forms for recipes, production orders, and manufacturing processes.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from core.forms import BaseModelForm
from .models import Recipe, RecipeItem, ProductionOrder, ProductionOrderItem
from inventory.models import Material, Product
from accounts.models import Employee


class RecipeForm(BaseModelForm):
    """Form for Recipe model."""
    
    class Meta:
        model = Recipe
        fields = [
            'code', 'name', 'description', 'product', 'version',
            'yield_quantity', 'estimated_time_minutes', 'complexity', 'status', 'instructions', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'placeholder': 'Código da receita'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'placeholder': 'Nome da receita'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descrição da receita'
            }),
            'product': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'version': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'placeholder': '1.0'
            }),
            'yield_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'step': '0.001',
                'min': '0.001'
            }),
            'estimated_time_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'min': '1'
            }),
            'complexity': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'rows': 8,
                'placeholder': 'Instruções passo a passo do preparo\nUse uma linha para cada etapa'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observações sobre a receita'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter products to only active ones
        self.fields['product'].queryset = Product.objects.filter(is_active=True)


class RecipeItemForm(forms.ModelForm):
    """Form for RecipeItem model."""
    
    class Meta:
        model = RecipeItem
        fields = ['recipe', 'material', 'quantity', 'order', 'notes']
        widgets = {
            'recipe': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'material': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'step': '0.001',
                'min': '0.001'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Observações sobre o material na receita'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter materials to only active ones
        self.fields['material'].queryset = Material.objects.filter(is_active=True)


class ProductionOrderForm(forms.ModelForm):
    """Form for ProductionOrder model."""
    
    class Meta:
        model = ProductionOrder
        fields = [
            'order_number', 'recipe', 'planned_quantity', 'priority', 
            'planned_start_date', 'planned_end_date', 'supervisor', 'notes'
        ]
        widgets = {
            'order_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'placeholder': 'Número da ordem de produção'
            }),
            'recipe': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'planned_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'step': '0.001',
                'min': '0.001'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'planned_start_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'type': 'datetime-local'
            }),
            'planned_end_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'type': 'datetime-local'
            }),
            'supervisor': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observações sobre a ordem de produção'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter employees to only active ones
        self.fields['supervisor'].queryset = Employee.objects.filter(is_active=True)
        
        # Set default start date to now
        if not self.instance.pk:
            self.fields['planned_start_date'].initial = timezone.now()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('planned_start_date')
        end_date = cleaned_data.get('planned_end_date')
        
        # Validate date range
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError({
                    'planned_end_date': 'A data de fim deve ser posterior à data de início.'
                })
            
            # Check if start date is not in the past (for new orders)
            if not self.instance.pk and start_date < timezone.now():
                raise ValidationError({
                    'planned_start_date': 'A data de início não pode ser no passado.'
                })
        
        return cleaned_data


class ProductionOrderItemForm(forms.ModelForm):
    """Form for ProductionOrderItem model."""
    
    class Meta:
        model = ProductionOrderItem
        fields = ['production_order', 'material', 'planned_quantity', 'consumed_quantity', 'unit_cost']
        widgets = {
            'production_order': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'material': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
            }),
            'planned_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'step': '0.001',
                'min': '0.001'
            }),
            'consumed_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'step': '0.001',
                'min': '0'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter materials to only active ones
        self.fields['material'].queryset = Material.objects.filter(is_active=True)


class ProductionOrderFilterForm(forms.Form):
    """Form for filtering production orders."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'placeholder': 'Buscar por número da ordem ou produto...'
        })
    )
    
    STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('planned', 'Planejado'),
        ('in_progress', 'Em Produção'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    
    PRIORITY_CHOICES = [
        ('', 'Todas as prioridades'),
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    
    responsible_employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        empty_label='Todos os responsáveis',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'type': 'date'
        })
    )
    
    ORDERING_CHOICES = [
        ('-created_at', 'Criação (mais recente)'),
        ('created_at', 'Criação (mais antigo)'),
        ('start_date', 'Data de início (mais próxima)'),
        ('-start_date', 'Data de início (mais distante)'),
        ('priority', 'Prioridade (baixa → alta)'),
        ('-priority', 'Prioridade (alta → baixa)'),
        ('order_number', 'Número da ordem (A-Z)'),
        ('-order_number', 'Número da ordem (Z-A)'),
    ]
    
    ordering = forms.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )


class ProductionOrderStatusUpdateForm(forms.Form):
    """Form for updating production order status."""
    
    STATUS_CHOICES = [
        ('planned', 'Planejado'),
        ('in_progress', 'Em Produção'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'rows': 2,
            'placeholder': 'Observações sobre a mudança de status...'
        })
    )


class MaterialRequirementCheckForm(forms.Form):
    """Form for checking material requirements for production."""
    
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    
    quantity = forms.DecimalField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'step': '0.01',
            'min': '0.01'
        })
    )


class ProductionReportForm(forms.Form):
    """Form for production reports."""
    
    REPORT_TYPE_CHOICES = [
        ('efficiency', 'Eficiência de Produção'),
        ('costs', 'Custos de Produção'),
        ('orders_status', 'Status dos Pedidos'),
        ('material_consumption', 'Consumo de Materiais'),
        ('recipe_analysis', 'Análise de Receitas'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'type': 'date'
        })
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    supervisor = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True, department='production'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
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


class BulkProductionOrderForm(forms.Form):
    """Form for creating multiple production orders."""
    
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.filter(status='active'),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    quantity_per_order = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=0.001,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'step': '0.001',
            'min': '0.001'
        })
    )
    number_of_orders = forms.IntegerField(
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'min': '1',
            'max': '50'
        })
    )
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'type': 'datetime-local'
        })
    )
    interval_hours = forms.IntegerField(
        min_value=1,
        max_value=168,  # 1 week
        initial=24,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'min': '1',
            'max': '168'
        }),
        help_text='Intervalo em horas entre cada ordem'
    )
    supervisor = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True, department='production'),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now():
            raise ValidationError('A data de início não pode ser no passado.')
        return start_date


class RecipeComparisonForm(forms.Form):
    """Form for comparing recipes."""
    
    recipe1 = forms.ModelChoiceField(
        queryset=Recipe.objects.filter(status='active'),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        }),
        label='Primeira receita'
    )
    recipe2 = forms.ModelChoiceField(
        queryset=Recipe.objects.filter(status='active'),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        }),
        label='Segunda receita'
    )

    def clean(self):
        cleaned_data = super().clean()
        recipe1 = cleaned_data.get('recipe1')
        recipe2 = cleaned_data.get('recipe2')
        
        if recipe1 and recipe2:
            if recipe1 == recipe2:
                raise ValidationError('Selecione receitas diferentes para comparação.')
        
        return cleaned_data
