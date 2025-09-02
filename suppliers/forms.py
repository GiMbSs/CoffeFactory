"""
Forms for suppliers app.
Forms for supplier management.
"""

from django import forms
from django.core.exceptions import ValidationError
import re

from core.forms import BaseModelForm
from .models import Supplier


class SupplierForm(BaseModelForm):
    """Form for Supplier model."""
    
    class Meta:
        model = Supplier
        fields = [
            'code', 'name', 'trade_name', 'supplier_type',
            'cnpj_cpf', 'state_registration', 'municipal_registration',
            'email', 'phone', 'mobile', 'website',
            'address', 'address_number', 'address_complement', 'neighborhood', 
            'city', 'state', 'postal_code', 'country', 
            'contact_person', 'contact_email', 'contact_phone',
            'payment_terms', 'credit_limit', 'notes', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'placeholder': 'Código do fornecedor'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome/Razão social'
            }),
            'trade_name': forms.TextInput(attrs={
                'placeholder': 'Nome fantasia'
            }),
            'supplier_type': forms.Select(),
            'cnpj_cpf': forms.TextInput(attrs={
                'placeholder': 'CNPJ ou CPF'
            }),
            'state_registration': forms.TextInput(attrs={
                'placeholder': 'Inscrição estadual'
            }),
            'municipal_registration': forms.TextInput(attrs={
                'placeholder': 'Inscrição municipal'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email principal'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefone'
            }),
            'mobile': forms.TextInput(attrs={
                'placeholder': 'Celular'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'Website'
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
                'placeholder': 'Estado'
            }),
            'postal_code': forms.TextInput(attrs={
                'placeholder': 'CEP'
            }),
            'country': forms.TextInput(attrs={
                'placeholder': 'País'
            }),
            'contact_person': forms.TextInput(attrs={
                'placeholder': 'Nome do contato'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'Email do contato'
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': 'Telefone do contato'
            }),
            'payment_terms': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Condições de pagamento'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'placeholder': 'Limite de crédito',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Observações'
            }),
            'is_active': forms.CheckboxInput(),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check for uniqueness excluding current instance
            if Supplier.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este código já está sendo utilizado.')
        return code

    def clean_cnpj_cpf(self):
        cnpj_cpf = self.cleaned_data.get('cnpj_cpf', '').strip()
        if cnpj_cpf:
            # Remove formatting characters
            cnpj_cpf_clean = re.sub(r'[^\d]', '', cnpj_cpf)
            
            supplier_type = self.cleaned_data.get('supplier_type')
            
            if supplier_type == 'company' and len(cnpj_cpf_clean) != 14:
                raise ValidationError('CNPJ deve ter 14 dígitos.')
            elif supplier_type == 'individual' and len(cnpj_cpf_clean) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            
            # Check for uniqueness excluding current instance
            if Supplier.objects.filter(cnpj_cpf=cnpj_cpf).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este CNPJ/CPF já está cadastrado.')
        
        return cnpj_cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check for uniqueness excluding current instance
            if Supplier.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este email já está sendo utilizado.')
        return email

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code', '').strip()
        if postal_code:
            # Remove formatting characters
            postal_code_clean = re.sub(r'[^\d]', '', postal_code)
            if len(postal_code_clean) != 8:
                raise ValidationError('CEP deve ter 8 dígitos.')
            # Format CEP
            return f"{postal_code_clean[:5]}-{postal_code_clean[5:]}"
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            # Remove formatting characters
            phone_clean = re.sub(r'[^\d]', '', phone)
            if len(phone_clean) < 10 or len(phone_clean) > 11:
                raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        return phone

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '').strip()
        if mobile:
            # Remove formatting characters
            mobile_clean = re.sub(r'[^\d]', '', mobile)
            if len(mobile_clean) < 10 or len(mobile_clean) > 11:
                raise ValidationError('Celular deve ter 10 ou 11 dígitos.')
        return mobile

    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get('contact_phone', '').strip()
        if contact_phone:
            # Remove formatting characters
            phone_clean = re.sub(r'[^\d]', '', contact_phone)
            if len(phone_clean) < 10 or len(phone_clean) > 11:
                raise ValidationError('Telefone do contato deve ter 10 ou 11 dígitos.')
        return contact_phone

    def clean_credit_limit(self):
        credit_limit = self.cleaned_data.get('credit_limit')
        if credit_limit is not None and credit_limit < 0:
            raise ValidationError('O limite de crédito não pode ser negativo.')
        return credit_limit


class SupplierSearchForm(forms.Form):
    """Form for searching suppliers."""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por nome, código, CNPJ/CPF...'
        })
    )
    supplier_type = forms.ChoiceField(
        choices=[('', 'Todos')] + Supplier.SUPPLIER_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('active', 'Ativos'),
            ('inactive', 'Inativos'),
        ],
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
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Estado'
        })
    )

    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if len(query) < 2 and query:
            raise ValidationError('A busca deve ter pelo menos 2 caracteres.')
        return query


class SupplierFilterForm(forms.Form):
    """Form for filtering suppliers."""
    
    supplier_type = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Supplier.SUPPLIER_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    has_credit_limit = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('yes', 'Com limite de crédito'),
            ('no', 'Sem limite de crédito'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    state = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Estado'
        })
    )
    is_active = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('true', 'Ativos'),
            ('false', 'Inativos'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class SupplierImportForm(forms.Form):
    """Form for importing suppliers from CSV/Excel."""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    has_header = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Arquivo possui cabeçalho'
    )
    update_existing = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Atualizar fornecedores existentes'
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('O arquivo deve ter no máximo 5MB.')
            
            # Check file extension
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            file_extension = '.' + file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(
                    f'Formato de arquivo não suportado. Use: {", ".join(allowed_extensions)}'
                )
        
        return file


class SupplierContactForm(forms.Form):
    """Form for supplier contact information update."""
    
    contact_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome do contato'
        })
    )
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email do contato'
        })
    )
    contact_phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Telefone do contato'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Observações sobre o contato'
        })
    )

    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get('contact_phone', '').strip()
        if contact_phone:
            # Remove formatting characters
            phone_clean = re.sub(r'[^\d]', '', contact_phone)
            if len(phone_clean) < 10 or len(phone_clean) > 11:
                raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        return contact_phone
