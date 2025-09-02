"""
Forms for core app.
Base forms and utilities.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone


class BaseForm(forms.Form):
    """Base form with common functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add TailwindCSS classes to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                })
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-4 h-4 text-coffee-600 bg-gray-100 border-gray-300 rounded focus:ring-coffee-500 dark:focus:ring-coffee-600 dark:bg-gray-700 dark:border-gray-600'
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                    'type': 'date'
                })
            elif isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                    'type': 'datetime-local'
                })
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                })


class BaseModelForm(forms.ModelForm):
    """Base model form with common functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add TailwindCSS classes to all fields (only if not already set)
        for field_name, field in self.fields.items():
            current_class = field.widget.attrs.get('class', '')
            # Only apply base classes if no custom class is already defined
            if not current_class or current_class in ['form-input', 'form-select', 'form-textarea', 'form-checkbox']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                    })
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                    })
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                    })
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.update({
                        'class': 'w-4 h-4 text-coffee-600 bg-gray-100 border-gray-300 rounded focus:ring-coffee-500 dark:focus:ring-coffee-600 dark:bg-gray-700 dark:border-gray-600'
                    })
                elif isinstance(field.widget, forms.DateInput):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                        'type': 'date'
                    })
                elif isinstance(field.widget, forms.DateTimeInput):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
                        'type': 'datetime-local'
                    })
                elif isinstance(field.widget, forms.NumberInput):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                    })
                elif isinstance(field.widget, forms.EmailInput):
                    field.widget.attrs.update({
                        'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
                    })


class SearchForm(BaseForm):
    """Generic search form."""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'placeholder': 'Buscar...'
        })
    )
    
    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if len(query) < 2 and query:
            raise ValidationError('A busca deve ter pelo menos 2 caracteres.')
        return query


class DateRangeForm(BaseForm):
    """Form for date range filtering."""
    
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
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('A data inicial deve ser anterior à data final.')
            
            if end_date > timezone.now().date():
                raise ValidationError('A data final não pode ser no futuro.')
        
        return cleaned_data


class FilterForm(BaseForm):
    """Generic filter form."""
    
    STATUS_CHOICES = [
        ('', 'Todos'),
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    
    def __init__(self, *args, **kwargs):
        # Allow dynamic status choices
        status_choices = kwargs.pop('status_choices', None)
        super().__init__(*args, **kwargs)
        
        if status_choices:
            self.fields['status'].choices = [('', 'Todos')] + list(status_choices)


class ConfirmationForm(BaseForm):
    """Form for confirmation dialogs."""
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.confirmation_message = kwargs.pop('confirmation_message', 'Confirmar ação?')
        super().__init__(*args, **kwargs)
        self.fields['confirm'].label = self.confirmation_message


class BulkActionForm(BaseForm):
    """Form for bulk actions."""
    
    ACTION_CHOICES = [
        ('activate', 'Ativar'),
        ('deactivate', 'Desativar'),
        ('delete', 'Excluir'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    selected_items = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        # Allow dynamic action choices
        action_choices = kwargs.pop('action_choices', None)
        super().__init__(*args, **kwargs)
        
        if action_choices:
            self.fields['action'].choices = action_choices
    
    def clean_selected_items(self):
        selected_items = self.cleaned_data.get('selected_items', '')
        if not selected_items:
            raise ValidationError('Selecione pelo menos um item.')
        
        try:
            # Convert comma-separated string to list of UUIDs
            item_ids = [item.strip() for item in selected_items.split(',') if item.strip()]
            if not item_ids:
                raise ValidationError('Selecione pelo menos um item.')
            return item_ids
        except Exception:
            raise ValidationError('IDs dos itens selecionados são inválidos.')


class ImportForm(BaseForm):
    """Form for importing data from files."""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    has_header = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-coffee-600 bg-gray-100 border-gray-300 rounded focus:ring-coffee-500 dark:focus:ring-coffee-600 dark:bg-gray-700 dark:border-gray-600'
        }),
        label='Arquivo possui cabeçalho'
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


class ExportForm(BaseForm):
    """Form for exporting data."""
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        initial='xlsx',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-coffee-500 focus:border-transparent'
        })
    )
    include_inactive = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-coffee-600 bg-gray-100 border-gray-300 rounded focus:ring-coffee-500 dark:focus:ring-coffee-600 dark:bg-gray-700 dark:border-gray-600'
        }),
        label='Incluir registros inativos'
    )
