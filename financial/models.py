"""
Financial models for coffee_factory project.
Models for accounts payable, receivable, and financial management.
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from core.models import BaseModel, AuditModel


class AccountsReceivable(AuditModel):
    """Accounts receivable model for tracking customer payments."""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('partially_paid', 'Parcialmente Pago'),
        ('paid', 'Pago'),
        ('overdue', 'Em Atraso'),
        ('written_off', 'Baixado'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Dinheiro'),
        ('check', 'Cheque'),
        ('bank_transfer', 'Transferência Bancária'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('promissory_note', 'Nota Promissória'),
        ('other', 'Outros'),
    ]
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número da fatura"
    )
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.PROTECT,
        related_name='receivables',
        help_text="Cliente"
    )
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receivables',
        help_text="Pedido de venda relacionado"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status do recebível"
    )
    
    # Financial information
    original_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Valor original"
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor pago"
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor de desconto concedido"
    )
    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor de juros"
    )
    fine_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor de multa"
    )
    
    # Dates
    issue_date = models.DateField(
        help_text="Data de emissão"
    )
    due_date = models.DateField(
        help_text="Data de vencimento"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data de pagamento"
    )
    
    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        help_text="Forma de pagamento"
    )
    bank_account = models.CharField(
        max_length=100,
        blank=True,
        help_text="Conta bancária de recebimento"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de referência (cheque, transferência, etc.)"
    )
    
    # Additional information
    description = models.CharField(
        max_length=200,
        help_text="Descrição"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Accounts Receivable'
        verbose_name_plural = 'Accounts Receivable'
        ordering = ['due_date', '-issue_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.get_display_name()}"

    @property
    def balance(self):
        """Calculate remaining balance."""
        return max(0, self.original_amount - self.paid_amount)

    @property
    def total_amount(self):
        """Calculate total amount including interest and fines."""
        return self.original_amount + self.interest_amount + self.fine_amount - self.discount_amount

    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        return timezone.now().date() > self.due_date and self.status in ['pending', 'partially_paid']

    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    def make_payment(self, amount, payment_method='', reference_number='', payment_date=None):
        """Process a payment for this receivable."""
        if payment_date is None:
            payment_date = timezone.now().date()
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if self.paid_amount + amount > self.total_amount:
            raise ValueError("Payment amount exceeds total amount")
        
        # Create payment record
        payment = AccountsReceivablePayment.objects.create(
            receivable=self,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            created_by=self.updated_by
        )
        
        # Update paid amount
        self.paid_amount += amount
        
        # Update status
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
            self.payment_date = payment_date
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        
        self.payment_method = payment_method
        if reference_number:
            self.reference_number = reference_number
        
        self.save()
        
        return payment


class AccountsReceivablePayment(BaseModel):
    """Payment records for accounts receivable."""
    
    receivable = models.ForeignKey(
        AccountsReceivable,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Conta a receber"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Valor do pagamento"
    )
    payment_date = models.DateField(
        help_text="Data do pagamento"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=AccountsReceivable.PAYMENT_METHOD_CHOICES,
        help_text="Forma de pagamento"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de referência"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Receivable Payment'
        verbose_name_plural = 'Receivable Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Pagamento {self.amount} - {self.receivable.invoice_number}"


class AccountsPayable(AuditModel):
    """Accounts payable model for tracking supplier payments."""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('partially_paid', 'Parcialmente Pago'),
        ('paid', 'Pago'),
        ('overdue', 'Em Atraso'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Dinheiro'),
        ('check', 'Cheque'),
        ('bank_transfer', 'Transferência Bancária'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('promissory_note', 'Nota Promissória'),
        ('other', 'Outros'),
    ]
    
    EXPENSE_TYPE_CHOICES = [
        ('material_purchase', 'Compra de Materiais'),
        ('equipment', 'Equipamentos'),
        ('maintenance', 'Manutenção'),
        ('utilities', 'Utilidades'),
        ('rent', 'Aluguel'),
        ('insurance', 'Seguro'),
        ('taxes', 'Impostos'),
        ('services', 'Serviços'),
        ('salaries', 'Salários'),
        ('benefits', 'Benefícios'),
        ('travel', 'Viagens'),
        ('marketing', 'Marketing'),
        ('office_supplies', 'Material de Escritório'),
        ('other', 'Outros'),
    ]
    
    invoice_number = models.CharField(
        max_length=50,
        help_text="Número da fatura do fornecedor"
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='payables',
        help_text="Fornecedor"
    )
    expense_type = models.CharField(
        max_length=30,
        choices=EXPENSE_TYPE_CHOICES,
        help_text="Tipo de despesa"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status do pagável"
    )
    
    # Financial information
    original_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Valor original"
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor pago"
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor de desconto obtido"
    )
    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor de juros"
    )
    fine_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor de multa"
    )
    
    # Dates
    invoice_date = models.DateField(
        help_text="Data da fatura"
    )
    due_date = models.DateField(
        help_text="Data de vencimento"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data de pagamento"
    )
    
    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        help_text="Forma de pagamento"
    )
    bank_account = models.CharField(
        max_length=100,
        blank=True,
        help_text="Conta bancária de pagamento"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de referência (cheque, transferência, etc.)"
    )
    
    # Additional information
    description = models.CharField(
        max_length=200,
        help_text="Descrição"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Accounts Payable'
        verbose_name_plural = 'Accounts Payable'
        ordering = ['due_date', '-invoice_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.name}"

    @property
    def balance(self):
        """Calculate remaining balance."""
        return max(0, self.original_amount - self.paid_amount)

    @property
    def total_amount(self):
        """Calculate total amount including interest and fines."""
        return self.original_amount + self.interest_amount + self.fine_amount - self.discount_amount

    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        return timezone.now().date() > self.due_date and self.status in ['pending', 'partially_paid']

    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    def make_payment(self, amount, payment_method='', reference_number='', payment_date=None):
        """Process a payment for this payable."""
        if payment_date is None:
            payment_date = timezone.now().date()
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if self.paid_amount + amount > self.total_amount:
            raise ValueError("Payment amount exceeds total amount")
        
        # Create payment record
        payment = AccountsPayablePayment.objects.create(
            payable=self,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            created_by=self.updated_by
        )
        
        # Update paid amount
        self.paid_amount += amount
        
        # Update status
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
            self.payment_date = payment_date
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        
        self.payment_method = payment_method
        if reference_number:
            self.reference_number = reference_number
        
        self.save()
        
        return payment


class AccountsPayablePayment(BaseModel):
    """Payment records for accounts payable."""
    
    payable = models.ForeignKey(
        AccountsPayable,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Conta a pagar"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Valor do pagamento"
    )
    payment_date = models.DateField(
        help_text="Data do pagamento"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=AccountsPayable.PAYMENT_METHOD_CHOICES,
        help_text="Forma de pagamento"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de referência"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Payable Payment'
        verbose_name_plural = 'Payable Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Pagamento {self.amount} - {self.payable.invoice_number}"


class Payroll(AuditModel):
    """Payroll model for employee salary management."""
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('calculated', 'Calculado'),
        ('approved', 'Aprovado'),
        ('paid', 'Pago'),
        ('cancelled', 'Cancelado'),
    ]
    
    payroll_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número da folha de pagamento"
    )
    employee = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.PROTECT,
        related_name='payrolls',
        help_text="Funcionário"
    )
    reference_month = models.DateField(
        help_text="Mês de referência (primeiro dia do mês)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Status da folha"
    )
    
    # Work information
    days_worked = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0)],
        help_text="Dias trabalhados"
    )
    hours_worked = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Horas trabalhadas"
    )
    overtime_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Horas extras"
    )
    
    # Earnings
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Salário base"
    )
    overtime_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Valor das horas extras"
    )
    bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Bonificações"
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Comissões"
    )
    other_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Outros proventos"
    )
    gross_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Salário bruto"
    )
    
    # Deductions
    inss_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="INSS"
    )
    irrf_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="IRRF"
    )
    health_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Plano de saúde"
    )
    dental_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Plano odontológico"
    )
    meal_voucher_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Desconto vale refeição"
    )
    transport_voucher_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Desconto vale transporte"
    )
    union_dues = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Contribuição sindical"
    )
    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Outros descontos"
    )
    total_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total de descontos"
    )
    
    # Final amounts
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Salário líquido"
    )
    
    # Payment information
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data de pagamento"
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Forma de pagamento"
    )
    bank_account = models.CharField(
        max_length=100,
        blank=True,
        help_text="Conta bancária"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Observações"
    )

    class Meta:
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        ordering = ['-reference_month', 'employee__user__first_name']
        unique_together = ['employee', 'reference_month']

    def __str__(self):
        return f"{self.payroll_number} - {self.employee.user.get_full_name()}"

    def calculate_gross_salary(self):
        """Calculate gross salary from base salary and earnings."""
        from decimal import Decimal
        
        self.gross_salary = (
            Decimal(str(self.base_salary or 0)) + 
            Decimal(str(self.overtime_amount or 0)) + 
            Decimal(str(self.bonus_amount or 0)) + 
            Decimal(str(self.commission_amount or 0)) + 
            Decimal(str(self.other_earnings or 0))
        )
        return self.gross_salary

    def calculate_deductions(self):
        """Calculate total deductions."""
        from decimal import Decimal
        
        self.total_deductions = (
            Decimal(str(self.inss_amount or 0)) +
            Decimal(str(self.irrf_amount or 0)) +
            Decimal(str(self.health_insurance or 0)) +
            Decimal(str(self.dental_insurance or 0)) +
            Decimal(str(self.meal_voucher_discount or 0)) +
            Decimal(str(self.transport_voucher_discount or 0)) +
            Decimal(str(self.union_dues or 0)) +
            Decimal(str(self.other_deductions or 0))
        )
        return self.total_deductions

    def calculate_net_salary(self):
        """Calculate net salary."""
        self.calculate_gross_salary()
        self.calculate_deductions()
        self.net_salary = self.gross_salary - self.total_deductions
        return self.net_salary

    def calculate_overtime(self, hourly_rate=None, overtime_multiplier=1.5):
        """Calculate overtime amount."""
        from decimal import Decimal
        
        if not hourly_rate and self.base_salary > 0:
            # Assume 220 working hours per month (8 hours x 22 working days)
            hourly_rate = self.base_salary / Decimal('220')
        
        if hourly_rate and self.overtime_hours > 0:
            self.overtime_amount = self.overtime_hours * hourly_rate * Decimal(str(overtime_multiplier))
        
        return self.overtime_amount

    def auto_calculate_taxes(self):
        """Auto-calculate INSS and IRRF based on Brazilian tax tables (simplified)."""
        # INSS calculation (2024 rates - simplified)
        if self.gross_salary <= 1412:
            inss_rate = 0.075
        elif self.gross_salary <= 2666.68:
            inss_rate = 0.09
        elif self.gross_salary <= 4000.03:
            inss_rate = 0.12
        else:
            inss_rate = 0.14
        
        self.inss_amount = min(self.gross_salary * inss_rate, 908.85)  # Max INSS 2024
        
        # IRRF calculation (simplified)
        taxable_income = self.gross_salary - self.inss_amount
        if taxable_income <= 2112:
            self.irrf_amount = 0
        elif taxable_income <= 2826.65:
            self.irrf_amount = (taxable_income * 0.075) - 158.40
        elif taxable_income <= 3751.05:
            self.irrf_amount = (taxable_income * 0.15) - 370.40
        elif taxable_income <= 4664.68:
            self.irrf_amount = (taxable_income * 0.225) - 651.73
        else:
            self.irrf_amount = (taxable_income * 0.275) - 884.96
        
        self.irrf_amount = max(0, self.irrf_amount)
        
        return self.inss_amount, self.irrf_amount

    def process_payroll(self):
        """Process complete payroll calculation."""
        # Calculate overtime if needed
        if self.overtime_hours > 0:
            self.calculate_overtime()
        
        # Calculate taxes
        self.auto_calculate_taxes()
        
        # Calculate final amounts
        self.calculate_net_salary()
        
        # Update status
        self.status = 'calculated'
        
        self.save()
        
        return self.net_salary
