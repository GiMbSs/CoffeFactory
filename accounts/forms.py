"""
Forms for accounts app.
User registration, authentication, and employee management forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, Employee


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with additional fields."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Sobrenome'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Telefone'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome de usuário'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirmar senha'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Este email já está sendo utilizado.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form."""
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_employee', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'is_employee': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Este email já está sendo utilizado.'))
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with email as username."""
    
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Senha'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class EmployeeForm(forms.ModelForm):
    """Form for Employee model."""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome de usuário'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Sobrenome'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Telefone'
        })
    )
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'department', 'position', 'employment_type',
            'salary', 'hire_date', 'address', 'emergency_contact', 
            'emergency_phone', 'notes', 'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ID do funcionário'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Cargo'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Salário',
                'step': '0.01'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Endereço completo',
                'rows': 3
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome do contato de emergência'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Telefone de emergência'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Observações adicionais',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        # Set is_active to True by default for new employees
        if not self.instance.pk:
            self.fields['is_active'].initial = True
        
        # Populate user fields if editing and user exists
        if self.instance.pk:
            try:
                if self.instance.user:
                    self.fields['username'].initial = self.instance.user.username
                    self.fields['email'].initial = self.instance.user.email
                    self.fields['first_name'].initial = self.instance.user.first_name
                    self.fields['last_name'].initial = self.instance.user.last_name
                    self.fields['phone'].initial = self.instance.user.phone
            except Employee.user.RelatedObjectDoesNotExist:
                # Employee doesn't have a user yet, which is fine for new instances
                pass

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exclude_id = None
        # Only get user ID if instance exists and has a user
        if self.instance.pk:
            try:
                if self.instance.user:
                    exclude_id = self.instance.user.pk
            except Employee.user.RelatedObjectDoesNotExist:
                # Employee doesn't have a user yet
                pass
        
        if User.objects.filter(email=email).exclude(pk=exclude_id).exists():
            raise ValidationError(_('Este email já está sendo utilizado.'))
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Este ID de funcionário já está sendo utilizado.'))
        return employee_id

    def save(self, commit=True):
        employee = super().save(commit=False)
        
        # Check if employee has a user (for editing) or needs one (for creation)
        has_user = False
        if employee.pk:
            try:
                has_user = bool(employee.user)
            except Employee.user.RelatedObjectDoesNotExist:
                has_user = False
        
        if not has_user:
            # Create new user if this is a new employee
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone=self.cleaned_data.get('phone', ''),
                is_employee=True
            )
            employee.user = user
        else:
            # Update existing user
            user = employee.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.phone = self.cleaned_data.get('phone', '')
            user.is_employee = True
            user.save()
        
        if commit:
            employee.save()
        return employee


class UserProfileForm(forms.ModelForm):
    """Form for user profile editing."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Sobrenome'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Telefone'
            }),
        }


class PasswordChangeForm(forms.Form):
    """Custom password change form."""
    
    old_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Senha atual'
        })
    )
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nova senha'
        })
    )
    new_password2 = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirmar nova senha'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError(_('Senha atual incorreta.'))
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError(_('As senhas não coincidem.'))
        
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
