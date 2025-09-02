"""
Suppliers models for coffee_factory project.
Simple supplier management for tracking vendors.
"""

from django.db import models
from django.core.validators import RegexValidator
from core.models import BaseModel


class Supplier(BaseModel):
    """Supplier model for vendor management."""
    
    SUPPLIER_TYPE_CHOICES = [
        ('individual', 'Pessoa Física'),
        ('company', 'Pessoa Jurídica'),
    ]
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código único do fornecedor"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nome/Razão social do fornecedor"
    )
    trade_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nome fantasia"
    )
    supplier_type = models.CharField(
        max_length=20,
        choices=SUPPLIER_TYPE_CHOICES,
        default='company',
        help_text="Tipo de fornecedor"
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
    municipal_registration = models.CharField(
        max_length=20,
        blank=True,
        help_text="Inscrição municipal"
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
    website = models.URLField(
        blank=True,
        help_text="Website"
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
    
    # Business information
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        help_text="Pessoa de contato"
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Email da pessoa de contato"
    )
    contact_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Telefone da pessoa de contato"
    )
    
    # Financial information
    payment_terms = models.CharField(
        max_length=100,
        blank=True,
        help_text="Condições de pagamento"
    )
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Limite de crédito"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )
    
    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
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

    def get_display_name(self):
        """Get the display name (trade name or name)."""
        return self.trade_name if self.trade_name else self.name
