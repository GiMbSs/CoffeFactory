"""
Inventory app views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.views import View
from django.utils import timezone

from .models import Category, Material, Product, StockMovement
from .forms import CategoryForm, MaterialForm, ProductForm


class InventoryDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal do inventory."""
    template_name = 'inventory/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas principais  
        context['total_materials'] = Material.objects.filter(is_active=True).count()
        context['total_products'] = Product.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.filter(is_active=True).count()
        
        # Para low_stock, vamos calcular diferente já que current_stock é uma property
        low_stock_materials = []
        for material in Material.objects.filter(is_active=True):
            if material.current_stock <= material.minimum_stock:
                low_stock_materials.append(material)
        context['low_stock_count'] = len(low_stock_materials)
        
        # Movimentações recentes
        context['recent_movements'] = StockMovement.objects.select_related(
            'material', 'product'
        ).order_by('-created_at')[:10]
        
        # Categorias mais usadas
        context['top_categories'] = Category.objects.annotate(
            material_count=Count('materials'),
            product_count=Count('products')
        ).filter(is_active=True).order_by('-material_count', '-product_count')[:5]
        
        return context


# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    """Lista de categorias."""
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        
        # Filtros
        search = self.request.GET.get('search')
        category_type = self.request.GET.get('type')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_type'] = self.request.GET.get('type', '')
        context['type_choices'] = Category.CATEGORY_TYPE_CHOICES
        
        # Estatísticas
        context['stats'] = {
            'total': Category.objects.filter(is_active=True).count(),
            'material_categories': Category.objects.filter(
                is_active=True, category_type='material'
            ).count(),
            'product_categories': Category.objects.filter(
                is_active=True, category_type='product'
            ).count(),
        }
        
        return context


class CategoryDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma categoria."""
    model = Category
    template_name = 'inventory/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Itens relacionados
        context['related_materials'] = category.materials.filter(is_active=True)[:10]
        context['related_products'] = category.products.filter(is_active=True)[:10]
        
        # Estatísticas
        context['stats'] = {
            'total_materials': category.materials.filter(is_active=True).count(),
            'total_products': category.products.filter(is_active=True).count(),
            'total_stock_value': sum(
                material.current_stock * material.cost_per_unit 
                for material in category.materials.filter(is_active=True)
            ),
        }
        
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Criação de categoria."""
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Edição de categoria."""
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    
    def get_success_url(self):
        return reverse_lazy('inventory:category_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Exclusão de categoria."""
    model = Category
    success_url = reverse_lazy('inventory:category_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Soft delete
        self.object.is_active = False
        self.object.save()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect(self.success_url)


# Material Views (placeholders)
class MaterialListView(LoginRequiredMixin, ListView):
    """Lista de materiais."""
    model = Material
    template_name = 'inventory/material_list.html'
    context_object_name = 'materials'


class MaterialDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um material."""
    model = Material
    template_name = 'inventory/material_detail.html'
    context_object_name = 'material'


class MaterialCreateView(LoginRequiredMixin, CreateView):
    """Criação de material."""
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'
    success_url = reverse_lazy('inventory:material_list')


class MaterialUpdateView(LoginRequiredMixin, UpdateView):
    """Edição de material."""
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'


# Product Views (placeholders)
class ProductListView(LoginRequiredMixin, ListView):
    """Lista de produtos."""
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um produto."""
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Criação de produto."""
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Edição de produto."""
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'


# Stock Movement Views
class StockMovementCreateView(LoginRequiredMixin, CreateView):
    """Criação de movimentação de estoque."""
    model = StockMovement
    template_name = 'inventory/stock_movement_form.html'
    fields = ['material', 'product', 'movement_type', 'quantity', 'reason', 'notes']
    success_url = reverse_lazy('inventory:dashboard')


# AJAX Views
class MaterialStockStatusView(LoginRequiredMixin, View):
    """API para status do estoque de materiais."""
    
    def get(self, request):
        materials = Material.objects.filter(is_active=True)
        
        low_stock = []
        for material in materials:
            if material.current_stock <= material.minimum_stock:
                low_stock.append({
                    'id': str(material.id),
                    'name': material.name,
                    'current_stock': material.current_stock,
                    'minimum_stock': material.minimum_stock,
                })
        
        return JsonResponse({
            'low_stock_materials': low_stock,
            'total_materials': materials.count(),
            'low_stock_count': len(low_stock),
        })


class InventoryStatsView(LoginRequiredMixin, View):
    """API para estatísticas do inventário."""
    
    def get(self, request):
        stats = {
            'total_materials': Material.objects.filter(is_active=True).count(),
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'low_stock_count': len([
                m for m in Material.objects.filter(is_active=True) 
                if m.current_stock <= m.minimum_stock
            ]),
            'recent_movements_count': StockMovement.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
        }
        
        return JsonResponse(stats)
