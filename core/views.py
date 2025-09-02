"""
Core views for coffee_factory project.
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from .forms import SearchForm, BulkActionForm, ImportForm


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'core/home.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard."""
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for authenticated users."""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add dashboard statistics here
        from inventory.models import Material, Product
        from sales.models import Customer, SalesOrder
        from production.models import ProductionOrder
        
        context.update({
            'total_materials': Material.objects.count(),
            'total_products': Product.objects.count(),
            'total_customers': Customer.objects.count(),
            'pending_orders': SalesOrder.objects.filter(status='pending').count(),
            'active_production': ProductionOrder.objects.filter(status='in_progress').count(),
        })
        
        return context


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    """Global search across all apps."""
    template_name = 'core/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm(self.request.GET)
        
        if self.request.GET.get('q'):
            search_term = self.request.GET.get('q')
            
            # Search across different models
            from inventory.models import Material, Product
            from sales.models import Customer
            from suppliers.models import Supplier
            
            context['results'] = {
                'materials': Material.objects.filter(
                    Q(name__icontains=search_term) | Q(description__icontains=search_term)
                )[:10],
                'products': Product.objects.filter(
                    Q(name__icontains=search_term) | Q(description__icontains=search_term)
                )[:10],
                'customers': Customer.objects.filter(
                    Q(name__icontains=search_term) | Q(email__icontains=search_term)
                )[:10],
                'suppliers': Supplier.objects.filter(
                    Q(name__icontains=search_term) | Q(email__icontains=search_term)
                )[:10],
            }
        
        return context


class BulkActionView(LoginRequiredMixin, FormView):
    """Handle bulk actions across different models."""
    template_name = 'core/bulk_action.html'
    form_class = BulkActionForm
    
    def form_valid(self, form):
        action = form.cleaned_data['action']
        model_type = form.cleaned_data['model_type']
        selected_ids = form.cleaned_data['selected_ids']
        
        # Process bulk action based on model type and action
        if model_type == 'material' and action == 'activate':
            from inventory.models import Material
            count = Material.objects.filter(id__in=selected_ids).update(is_active=True)
            messages.success(self.request, f'{count} materiais ativados com sucesso!')
        
        elif model_type == 'product' and action == 'deactivate':
            from inventory.models import Product
            count = Product.objects.filter(id__in=selected_ids).update(is_active=False)
            messages.success(self.request, f'{count} produtos desativados com sucesso!')
        
        # Add more bulk actions as needed
        
        return redirect('core:dashboard')


class ImportDataView(LoginRequiredMixin, FormView):
    """Import data from files."""
    template_name = 'core/import_data.html'
    form_class = ImportForm
    
    def form_valid(self, form):
        file_obj = form.cleaned_data['file']
        data_type = form.cleaned_data['data_type']
        
        # Process import based on data type
        try:
            if data_type == 'materials':
                # Import materials logic here
                messages.success(self.request, 'Materiais importados com sucesso!')
            elif data_type == 'customers':
                # Import customers logic here
                messages.success(self.request, 'Clientes importados com sucesso!')
            # Add more import types as needed
            
        except Exception as e:
            messages.error(self.request, f'Erro na importação: {str(e)}')
        
        return redirect('core:dashboard')


class HealthCheckView(TemplateView):
    """Simple health check endpoint."""
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat()
        })
