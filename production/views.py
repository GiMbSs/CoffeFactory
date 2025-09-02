"""
Production views for coffee_factory project.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum, F, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Recipe, RecipeItem, ProductionOrder, ProductionOrderItem
from .forms import (
    RecipeForm, RecipeItemForm, ProductionOrderForm, ProductionOrderItemForm,
    ProductionReportForm, BulkProductionOrderForm, RecipeComparisonForm
)
from inventory.models import Material, Product


class ProductionDashboardView(LoginRequiredMixin, TemplateView):
    """Production dashboard view."""
    template_name = 'production/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get production statistics
        today = timezone.now().date()
        context['stats'] = {
            'total_orders': ProductionOrder.objects.count(),
            'orders_today': ProductionOrder.objects.filter(planned_start_date__date=today).count(),
            'active_orders': ProductionOrder.objects.filter(status__in=['planned', 'in_progress']).count(),
            'completed_orders': ProductionOrder.objects.filter(status='completed').count(),
        }
        
        # Recent orders for dashboard
        context['recent_orders'] = ProductionOrder.objects.select_related(
            'recipe', 'recipe__product', 'supervisor'
        ).order_by('-created_at')[:5]
        
        # Recent recipes for dashboard  
        from .models import Recipe
        context['recent_recipes'] = Recipe.objects.select_related(
            'product'
        ).filter(status='active').order_by('-created_at')[:5]
        
        return context


class ProductionOrderListView(LoginRequiredMixin, ListView):
    """Production order list view."""
    model = ProductionOrder
    template_name = 'production/production_order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        queryset = ProductionOrder.objects.select_related(
            'recipe', 'recipe__product', 'supervisor'
        ).all()
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(recipe__product__name__icontains=search)
            ).distinct()
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Priority filter
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Date range filter
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(planned_start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(planned_end_date__lte=end_date)
        
        # Ordering
        ordering = self.request.GET.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Organize orders by status for kanban view
        all_orders = self.get_queryset()
        context['orders_by_status'] = {
            'planned': all_orders.filter(status='planned'),
            'in_progress': all_orders.filter(status='in_progress'),
            'completed': all_orders.filter(status='completed'),
        }
        
        # Get statistics
        context['stats'] = {
            'total_orders': all_orders.count(),
            'planned_orders': all_orders.filter(status='planned').count(),
            'in_progress_orders': all_orders.filter(status='in_progress').count(),
            'completed_orders': all_orders.filter(status='completed').count(),
            'high_priority_orders': all_orders.filter(priority='high').count(),
        }
        
        # Get filter options
        from accounts.models import Employee
        context['employees'] = Employee.objects.filter(is_active=True)
        
        return context


class ProductionOrderDetailView(LoginRequiredMixin, DetailView):
    """Production order detail view."""
    model = ProductionOrder
    template_name = 'production/production_order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Get order items with products and recipes
        context['order_items'] = order.items.select_related(
            'product', 'product__recipe'
        ).all()
        
        # Calculate production progress
        total_items = order.items.count()
        completed_items = order.items.filter(status='completed').count()
        context['progress_percentage'] = (completed_items / total_items * 100) if total_items > 0 else 0
        
        # Get material requirements
        context['material_requirements'] = self.get_material_requirements(order)
        
        return context
    
    def get_material_requirements(self, order):
        """Calculate total material requirements for the order."""
        requirements = {}
        
        for item in order.items.all():
            if hasattr(item.product, 'recipe') and item.product.recipe:
                for ingredient in item.product.recipe.ingredients.all():
                    material = ingredient.material
                    required_quantity = ingredient.quantity_per_unit * item.quantity
                    
                    if material in requirements:
                        requirements[material] += required_quantity
                    else:
                        requirements[material] = required_quantity
        
        # Add availability check
        material_requirements = {}
        for material, required in requirements.items():
            material_requirements[material] = {
                'required': required,
                'available': material.current_stock,
                'sufficient': material.current_stock >= required
            }
        
        return material_requirements


# AJAX Views
class ProductionOrderStatusUpdateView(LoginRequiredMixin, TemplateView):
    """AJAX view to update production order status."""
    
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        try:
            order = ProductionOrder.objects.get(id=order_id)
            old_status = order.status
            order.status = new_status
            
            # Update timestamps based on status
            if new_status == 'in_progress' and old_status == 'planned':
                order.actual_start_date = timezone.now()
            elif new_status == 'completed':
                order.actual_end_date = timezone.now()
            
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status atualizado para {order.get_status_display()}'
            })
        
        except ProductionOrder.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Ordem de produção não encontrada'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar status: {str(e)}'
            })


class ProductionOrderCreateView(LoginRequiredMixin, CreateView):
    """Production order create view."""
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = 'production/production_order_form.html'
    success_url = reverse_lazy('production:production_order_list')


class ProductionOrderUpdateView(LoginRequiredMixin, UpdateView):
    """Production order update view."""
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = 'production/production_order_form.html'
    success_url = reverse_lazy('production:production_order_list')


class RecipeListView(LoginRequiredMixin, ListView):
    """Recipe list view."""
    model = Recipe
    template_name = 'production/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 20

    def get_queryset(self):
        # Return empty queryset for now
        return []


class RecipeCreateView(LoginRequiredMixin, CreateView):
    """Recipe create view."""
    model = Recipe
    form_class = RecipeForm
    template_name = 'production/recipe_form.html'
    success_url = reverse_lazy('production:recipe_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Receita "{form.instance.name}" criada com sucesso!')
        return super().form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    """Recipe update view."""
    model = Recipe
    form_class = RecipeForm
    template_name = 'production/recipe_form.html'
    success_url = reverse_lazy('production:recipe_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Receita "{form.instance.name}" atualizada com sucesso!')
        return super().form_valid(form)


class RecipeDetailView(LoginRequiredMixin, DetailView):
    """Recipe detail view."""
    model = Recipe
    template_name = 'production/recipe_detail.html'
    context_object_name = 'recipe'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()
        
        # Get recipe items
        context['recipe_items'] = recipe.recipe_items.select_related('material').all()
        context['total_cost'] = recipe.total_material_cost
        context['cost_per_unit'] = recipe.cost_per_unit
        
        return context


class RecipeItemCreateView(LoginRequiredMixin, CreateView):
    """Recipe item create view."""
    model = RecipeItem
    form_class = RecipeItemForm
    template_name = 'production/recipe_item_form.html'
    
    def get_success_url(self):
        return reverse_lazy('production:recipe_detail', kwargs={'pk': self.object.recipe.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Item adicionado à receita com sucesso!')
        return super().form_valid(form)


class ProductionReportsView(LoginRequiredMixin, TemplateView):
    """Production reports view."""
    template_name = 'production/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductionReportForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ProductionReportForm(request.POST)
        if form.is_valid():
            # Process report generation here
            messages.success(request, 'Relatório gerado com sucesso!')
        return self.render_to_response({'form': form})


class BulkProductionOrderView(LoginRequiredMixin, TemplateView):
    """Bulk production order creation view."""
    template_name = 'production/bulk_order_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BulkProductionOrderForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = BulkProductionOrderForm(request.POST)
        if form.is_valid():
            # Process bulk order creation here
            messages.success(request, 'Ordens de produção criadas com sucesso!')
            return redirect('production:order_list')
        return self.render_to_response({'form': form})


class RecipeComparisonView(LoginRequiredMixin, TemplateView):
    """Recipe comparison view."""
    template_name = 'production/recipe_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RecipeComparisonForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = RecipeComparisonForm(request.POST)
        if form.is_valid():
            recipe1 = form.cleaned_data['recipe1']
            recipe2 = form.cleaned_data['recipe2']
            
            context = {
                'form': form,
                'recipe1': recipe1,
                'recipe2': recipe2,
                'recipe1_items': recipe1.recipe_items.select_related('material').all(),
                'recipe2_items': recipe2.recipe_items.select_related('material').all(),
            }
            return self.render_to_response(context)
        
        return self.render_to_response({'form': form})
    template_name = 'production/recipe_detail.html'
    context_object_name = 'recipe'
