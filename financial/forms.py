"""
Forms for financial app.
Forms for accounts receivable, payable, and financial management.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from core.forms import BaseModelForm
from .models import (
    AccountsReceivable, AccountsReceivablePayment,
    AccountsPayable, AccountsPayablePayment, Payroll
)


class AccountsReceivableForm(BaseModelForm):
    """Form for AccountsReceivable model."""
    
    class Meta:
        model = AccountsReceivable
        fields = [
            'invoice_number', 'customer', 'sales_order', 'status',
            'original_amount', 'issue_date', 'due_date', 'payment_method', 'description', 'notes'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Número da fatura'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sales_order': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'original_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Descrição da conta a receber'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Observações'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')
        
        if issue_date and due_date:
            if due_date < issue_date:
                raise ValidationError({
                    'due_date': 'A data de vencimento deve ser posterior à data de emissão.'
                })
        
        return cleaned_data


class AccountsPayableForm(BaseModelForm):
    """Form for AccountsPayable model."""
    
    class Meta:
        model = AccountsPayable
        fields = [
            'invoice_number', 'supplier', 'expense_type', 'status', 'original_amount',
            'invoice_date', 'due_date', 'payment_method', 'description', 'notes'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Número da fatura'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expense_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'original_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'invoice_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Descrição da conta a pagar'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Observações'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        invoice_date = cleaned_data.get('invoice_date')
        due_date = cleaned_data.get('due_date')
        
        if invoice_date and due_date:
            if due_date < invoice_date:
                raise ValidationError({
                    'due_date': 'A data de vencimento deve ser posterior à data da fatura.'
                })
        
        return cleaned_data


class PayrollForm(BaseModelForm):
    """Form for Payroll model."""
    
    class Meta:
        model = Payroll
        fields = [
            'payroll_number', 'employee', 'reference_month', 'status',
            'days_worked', 'hours_worked', 'overtime_hours', 'base_salary',
            'overtime_amount', 'bonus_amount', 'commission_amount', 'notes'
        ]
        widgets = {
            'payroll_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Número da folha'
            }),
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference_month': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'days_worked': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'max': '31'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.5',
                'min': '0'
            }),
            'overtime_hours': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.5',
                'min': '0'
            }),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'overtime_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'bonus_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'commission_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Observações sobre a folha de pagamento'
            }),
        }


class FinancialReportForm(forms.Form):
    """Form for financial reports."""
    
    REPORT_TYPE_CHOICES = [
        ('receivables', 'Contas a Receber'),
        ('payables', 'Contas a Pagar'),
        ('payroll', 'Folha de Pagamento'),
        ('cash_flow', 'Fluxo de Caixa'),
        ('financial_summary', 'Resumo Financeiro'),
    ]
    
    report_type = forms.ChoiceField(
        label='Tipo de Relatório',
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    start_date = forms.DateField(
        label='Data Inicial',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        label='Data Final',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    include_paid = forms.BooleanField(
        label='Incluir itens pagos',
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
                raise ValidationError({
                    'end_date': 'A data final deve ser posterior à data inicial.'
                })
        
        return cleaned_data
