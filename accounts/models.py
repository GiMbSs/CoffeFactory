"""
User models for coffee_factory project.
Custom user model and related user management.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from core.models import BaseModel


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses UUID as primary key and adds custom fields.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address for login and communication"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Contact phone number"
    )
    is_employee = models.BooleanField(
        default=False,
        help_text="Whether this user is an employee"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Make email the primary identifier for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username


class Employee(BaseModel):
    """
    Employee model for managing staff information and payroll.
    """
    DEPARTMENT_CHOICES = [
        ('production', 'Produção'),
        ('sales', 'Vendas'),
        ('admin', 'Administração'),
        ('quality', 'Controle de Qualidade'),
        ('maintenance', 'Manutenção'),
        ('warehouse', 'Estoque'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Tempo Integral'),
        ('part_time', 'Meio Período'),
        ('contract', 'Contrato'),
        ('intern', 'Estágio'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        help_text="Associated user account"
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Employee identification number"
    )
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        help_text="Department where the employee works"
    )
    position = models.CharField(
        max_length=100,
        help_text="Job position/title"
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        help_text="Type of employment"
    )
    hire_date = models.DateField(
        help_text="Date when the employee was hired"
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly salary in Brazilian Real"
    )
    address = models.TextField(
        blank=True,
        help_text="Employee address"
    )
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emergency contact person"
    )
    emergency_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Emergency contact phone"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the employee"
    )

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()} ({self.department})"

    def save(self, *args, **kwargs):
        """Override save to mark user as employee."""
        if not self.user.is_employee:
            self.user.is_employee = True
            self.user.save()
        super().save(*args, **kwargs)
