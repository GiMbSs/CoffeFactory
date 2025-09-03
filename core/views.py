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
        from financial.models import AccountsReceivable, AccountsPayable
        from django.db.models import Sum, Count, Q
        from decimal import Decimal
        import datetime
        
        # Calculate date ranges
        today = timezone.now().date()
        last_month = today.replace(day=1) - datetime.timedelta(days=1)
        this_month_start = today.replace(day=1)
        last_month_start = last_month.replace(day=1)
        
        # Production Orders
        production_orders = ProductionOrder.objects.filter(status='in_progress').count()
        total_production_orders = ProductionOrder.objects.count()
        production_capacity_used = (production_orders / max(total_production_orders, 1)) * 100 if total_production_orders > 0 else 0
        
        # Inventory Statistics
        total_products = Product.objects.count()
        # Contagem de produtos com baixo estoque (usando propriedade current_stock)
        products_with_stock = []
        for product in Product.objects.all():
            if product.current_stock <= product.minimum_stock or product.current_stock <= 10:
                products_with_stock.append(product)
        products_low_stock = len(products_with_stock)
        
        # Sales Statistics  
        this_month_sales = SalesOrder.objects.filter(
            order_date__gte=this_month_start,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        last_month_sales = SalesOrder.objects.filter(
            order_date__gte=last_month_start,
            order_date__lt=this_month_start,
            status='completed'  
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        sales_growth = 0
        if last_month_sales > 0:
            sales_growth = ((this_month_sales - last_month_sales) / last_month_sales) * 100
        
        # Sales goal (configurable via system settings)
        from .system_config import SystemConfig
        monthly_sales_goal = SystemConfig.get_monthly_sales_goal()
        sales_goal_percentage = (this_month_sales / monthly_sales_goal) * 100 if monthly_sales_goal > 0 else 0
        
        # Financial Statistics
        accounts_receivable = AccountsReceivable.objects.filter(
            status='pending'
        ).aggregate(total=Sum('original_amount'))['total'] or Decimal('0')
        
        accounts_payable = AccountsPayable.objects.filter(
            status='pending'
        ).aggregate(total=Sum('original_amount'))['total'] or Decimal('0')
        
        cash_flow = accounts_receivable - accounts_payable
        
        # Recent Activities (last 10)
        recent_orders = SalesOrder.objects.select_related('customer').order_by('-created_at')[:5]
        recent_production = ProductionOrder.objects.select_related('recipe__product').order_by('-created_at')[:3]
        
        # Notifications
        notifications = []
        
        # Stock alerts
        if products_low_stock > 0:
            notifications.append({
                'type': 'warning',
                'title': 'Estoque Baixo',
                'message': f'{products_low_stock} produtos com estoque abaixo do mínimo',
                'url': 'inventory:product_list',
                'icon': 'fas fa-exclamation-triangle'
            })
        
        # Pending payments
        due_payments = AccountsPayable.objects.filter(
            due_date__lte=today + datetime.timedelta(days=3),
            status='pending'
        ).count()
        
        if due_payments > 0:
            notifications.append({
                'type': 'info',
                'title': 'Vencimentos Próximos',
                'message': f'{due_payments} contas a pagar vencem em 3 dias',
                'url': 'financial:accounts_payable',
                'icon': 'fas fa-clock'
            })
        
        # Sales goal achievement
        if sales_goal_percentage >= 90:
            notifications.append({
                'type': 'success',
                'title': 'Meta de Vendas',
                'message': f'{sales_goal_percentage:.0f}% da meta mensal alcançada',
                'url': 'sales:dashboard',
                'icon': 'fas fa-trophy'
            })
        
        context.update({
            # KPI Data
            'production_orders': production_orders,
            'production_capacity_used': min(production_capacity_used, 100),
            'total_products': total_products,
            'products_low_stock': products_low_stock,
            'this_month_sales': this_month_sales,
            'sales_growth': sales_growth,
            'sales_goal_percentage': min(sales_goal_percentage, 100),
            'cash_flow': cash_flow,
            'accounts_receivable': accounts_receivable,
            'accounts_payable': accounts_payable,
            
            # Activities
            'recent_orders': recent_orders,
            'recent_production': recent_production,
            
            # Notifications
            'notifications': notifications,
            'notification_count': len(notifications),
            
            # Additional counts
            'total_materials': Material.objects.count(),
            'total_customers': Customer.objects.count(),
            'pending_orders': SalesOrder.objects.filter(status='pending').count(),
            'active_production': production_orders,
        })
        
        # Chart data - Generate dynamic data for charts
        from .system_config import SystemConfig
        chart_defaults = SystemConfig.get_chart_defaults()
        
        # Sales chart data (last 9 months)
        sales_months = []
        sales_data = []
        
        for i in range(8, -1, -1):  # Last 9 months
            month_date = today.replace(day=1) - datetime.timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
            
            month_sales = SalesOrder.objects.filter(
                order_date__gte=month_start,
                order_date__lt=next_month,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            sales_months.append(chart_defaults['sales_chart_months'][month_start.month - 1])
            sales_data.append(float(month_sales))
        
        # Production chart data - Get actual production by category/product type
        from inventory.models import Product
        from production.models import ProductionOrder
        production_labels = []
        production_data = []
        
        # Get top 5 products by recent production orders
        recent_production_orders = ProductionOrder.objects.filter(
            created_at__gte=today - datetime.timedelta(days=30),
            status__in=['completed', 'in_progress']
        ).select_related('recipe__product')
        
        # Count production by product
        product_production_count = {}
        for order in recent_production_orders:
            product_name = order.recipe.product.name
            if product_name in product_production_count:
                product_production_count[product_name] += float(order.produced_quantity or order.planned_quantity)
            else:
                product_production_count[product_name] = float(order.produced_quantity or order.planned_quantity)
        
        # Sort by production quantity and get top 5
        sorted_products = sorted(product_production_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for product_name, quantity in sorted_products:
            production_labels.append(product_name)
            production_data.append(int(quantity))
        
        # Fallback to default data if no production data
        if not production_labels:
            production_labels = chart_defaults['production_categories'][:5]
            production_data = [35, 25, 20, 12, 8]  # Default fallback data
        
        context.update({
            # Chart data
            'sales_chart_labels': sales_months,
            'sales_chart_data': sales_data,
            'production_chart_labels': production_labels,
            'production_chart_data': production_data,
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


class SettingsView(LoginRequiredMixin, TemplateView):
    """System settings view."""
    template_name = 'core/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Configurações do Sistema'
        return context


class HelpView(TemplateView):
    """Help page view."""
    template_name = 'core/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Central de Ajuda'
        return context


class SupportView(TemplateView):
    """Support page view."""
    template_name = 'core/support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Suporte Técnico'
        return context


class DocumentationView(TemplateView):
    """Documentation page view."""
    template_name = 'core/documentation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Documentação'
        return context
