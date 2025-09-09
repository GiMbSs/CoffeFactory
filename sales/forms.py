"""
Forms for sales app.
Forms for customers, sales orders, and sales management.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re

from core.forms import BaseModelForm
from .models import Customer, SalesOrder, SalesOrderItem
from inventory.models import Product


class CustomerForm(BaseModelForm):
    """Form for Customer model."""
    
    class Meta:
        model = Customer
        fields = [
            'code', 'name', 'trade_name', 'customer_type', 'status', 'cnpj_cpf', 
            'state_registration', 'email', 'phone', 'mobile', 'address', 
            'address_number', 'address_complement', 'neighborhood', 'city', 
            'state', 'postal_code', 'credit_limit', 'payment_terms', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'placeholder': 'Código do cliente'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome completo ou razão social'
            }),
            'trade_name': forms.TextInput(attrs={
                'placeholder': 'Nome fantasia'
            }),
            'customer_type': forms.Select(),
            'status': forms.Select(),
            'cnpj_cpf': forms.TextInput(attrs={
                'placeholder': 'CPF ou CNPJ'
            }),
            'state_registration': forms.TextInput(attrs={
                'placeholder': 'Inscrição estadual'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'email@exemplo.com'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '(11) 99999-9999'
            }),
            'mobile': forms.TextInput(attrs={
                'placeholder': '(11) 99999-9999'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Endereço'
            }),
            'address_number': forms.TextInput(attrs={
                'placeholder': 'Número'
            }),
            'address_complement': forms.TextInput(attrs={
                'placeholder': 'Complemento'
            }),
            'neighborhood': forms.TextInput(attrs={
                'placeholder': 'Bairro'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Cidade'
            }),
            'state': forms.TextInput(attrs={
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'postal_code': forms.TextInput(attrs={
                'placeholder': 'CEP'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'payment_terms': forms.NumberInput(attrs={
                'min': '1'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Observações sobre o cliente'
            }),
        }
    
    def clean_cnpj_cpf(self):
        cnpj_cpf = self.cleaned_data.get('cnpj_cpf')
        customer_type = self.cleaned_data.get('customer_type')
        
        if cnpj_cpf:
            # Remove non-numeric characters
            cnpj_cpf = ''.join(filter(str.isdigit, cnpj_cpf))
            
            # Basic validation for CPF/CNPJ length
            if customer_type == 'individual' and len(cnpj_cpf) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            elif customer_type == 'company' and len(cnpj_cpf) != 14:
                raise ValidationError('CNPJ deve ter 14 dígitos.')
            
            return cnpj_cpf
class SalesOrderForm(forms.ModelForm):
    """Form for SalesOrder model."""
    
    class Meta:
        model = SalesOrder
        fields = [
            'order_number', 'customer', 'status',
            'priority', 'delivery_date', 'payment_method', 'payment_terms', 
            'discount_percentage', 'notes'
        ]
        labels = {
            'order_number': 'Número do Pedido',
            'customer': 'Cliente',
            'status': 'Status',
            'priority': 'Prioridade',
            'delivery_date': 'Data de Entrega',
            'payment_method': 'Forma de Pagamento',
            'payment_terms': 'Condições de Pagamento',
            'discount_percentage': 'Desconto (%)',
            'notes': 'Observações'
        }
        widgets = {
            'order_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Número do pedido'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: PIX, Cartão, Dinheiro'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: À vista, 30 dias'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Observações sobre o pedido'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter customers to only active ones
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        
        # Make discount_percentage optional with default value
        self.fields['discount_percentage'].required = False
        self.fields['discount_percentage'].initial = 0
        
        # Make order_number optional for auto-generation
        self.fields['order_number'].required = False
        
        # Make payment fields optional
        self.fields['payment_method'].required = False
        self.fields['payment_terms'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_date = cleaned_data.get('delivery_date')
        
        # Validate delivery date is not in the past
        if delivery_date and delivery_date < timezone.now().date():
            raise ValidationError({
                'delivery_date': 'A data de entrega não pode ser no passado.'
            })
        
        return cleaned_data


class SalesOrderItemForm(forms.ModelForm):
    """Form for SalesOrderItem model."""
    
    class Meta:
        model = SalesOrderItem
        fields = ['product', 'quantity', 'unit_price', 'discount_percentage']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter products to only active ones
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Auto-populate unit price if product is selected
        if self.instance.pk and self.instance.product:
            self.fields['unit_price'].initial = self.instance.product.sale_price


class SalesOrderFilterForm(forms.Form):
    """Form for filtering sales orders."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por número, cliente ou produto...'
        })
    )
    
    STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('in_production', 'Em Produção'),
        ('ready', 'Pronto'),
        ('delivered', 'Entregue'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        empty_label='Todos os clientes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    PAYMENT_STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('pending', 'Pendente'),
        ('partial', 'Parcial'),
        ('paid', 'Pago'),
        ('overdue', 'Vencido'),
    ]
    
    payment_status = forms.ChoiceField(
        choices=PAYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    DELIVERY_STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('pending', 'Pendente'),
        ('preparing', 'Preparando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
    ]
    
    delivery_status = forms.ChoiceField(
        choices=DELIVERY_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
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
    
    ORDERING_CHOICES = [
        ('-order_date', 'Data do pedido (mais recente)'),
        ('order_date', 'Data do pedido (mais antigo)'),
        ('-total_amount', 'Valor (maior)'),
        ('total_amount', 'Valor (menor)'),
        ('customer__name', 'Cliente (A-Z)'),
        ('-customer__name', 'Cliente (Z-A)'),
        ('order_number', 'Número do pedido (A-Z)'),
        ('-order_number', 'Número do pedido (Z-A)'),
        ('status', 'Status (A-Z)'),
        ('-status', 'Status (Z-A)'),
    ]
    
    ordering = forms.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        initial='-order_date',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CustomerFilterForm(forms.Form):
    """Form for filtering customers."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por nome, documento, email ou telefone...'
        })
    )
    
    CUSTOMER_TYPE_CHOICES = [
        ('', 'Todos os tipos'),
        ('pf', 'Pessoa Física'),
        ('pj', 'Pessoa Jurídica'),
    ]
    
    customer_type = forms.ChoiceField(
        choices=CUSTOMER_TYPE_CHOICES,
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
        ('customer_type', 'Tipo (A-Z)'),
        ('-customer_type', 'Tipo (Z-A)'),
        ('created_at', 'Criação (antigo)'),
        ('-created_at', 'Criação (recente)'),
    ]
    
    ordering = forms.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        initial='name',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class SalesOrderStatusUpdateForm(forms.Form):
    """Form for updating sales order status."""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('in_production', 'Em Produção'),
        ('ready', 'Pronto'),
        ('delivered', 'Entregue'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 2,
            'placeholder': 'Observações sobre a mudança de status...'
        })
    )


class SalesReportForm(forms.Form):
    """Form for sales reports."""
    
    REPORT_TYPE_CHOICES = [
        ('sales_summary', 'Resumo de Vendas'),
        ('customer_analysis', 'Análise de Clientes'),
        ('product_performance', 'Performance de Produtos'),
        ('sales_rep_performance', 'Performance de Vendedores'),
        ('revenue_analysis', 'Análise de Receita'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError('A data final deve ser posterior à data inicial.')
        
        return cleaned_data


class CustomerCreditForm(forms.Form):
    """Form for managing customer credit."""
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    new_credit_limit = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'min': '0'
        })
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Motivo da alteração do limite de crédito'
        })
    )


class BulkOrderStatusForm(forms.Form):
    """Form for bulk order status updates."""
    
    STATUS_CHOICES = [
        ('processing', 'Em Processamento'),
        ('confirmed', 'Confirmado'),
        ('in_production', 'Em Produção'),
        ('ready_for_delivery', 'Pronto para Entrega'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
    ]
    
    new_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    selected_orders = forms.CharField(
        widget=forms.HiddenInput()
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Observações sobre a alteração de status'
        })
    )

    def clean_selected_orders(self):
        selected_orders = self.cleaned_data.get('selected_orders', '')
        if not selected_orders:
            raise ValidationError('Selecione pelo menos um pedido.')
        
        try:
            # Convert comma-separated string to list of UUIDs
            order_ids = [order.strip() for order in selected_orders.split(',') if order.strip()]
            if not order_ids:
                raise ValidationError('Selecione pelo menos um pedido.')
            return order_ids
        except Exception:
            raise ValidationError('IDs dos pedidos selecionados são inválidos.')


class CustomerSearchForm(forms.Form):
    """Form for searching customers."""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por nome, código, email, CNPJ/CPF...'
        })
    )
    customer_type = forms.ChoiceField(
        choices=[('', 'Todos')] + Customer.CUSTOMER_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + Customer.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Cidade'
        })
    )
    state = forms.CharField(
        max_length=2,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'UF'
        })
    )

    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if len(query) < 2 and query:
            raise ValidationError('A busca deve ter pelo menos 2 caracteres.')
        return query

    def clean_state(self):
        state = self.cleaned_data.get('state', '').strip().upper()
        if state and len(state) != 2:
            raise ValidationError('O estado deve ter 2 caracteres.')
        return state


class SalesOrderSearchForm(forms.Form):
    """Form for searching sales orders."""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por número do pedido, cliente...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + SalesOrder.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    priority = forms.ChoiceField(
        choices=[('', 'Todas')] + SalesOrder.PRIORITY_CHOICES,
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
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if len(query) < 2 and query:
            raise ValidationError('A busca deve ter pelo menos 2 caracteres.')
        return query

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError('A data final deve ser posterior à data inicial.')
        
        return cleaned_data
