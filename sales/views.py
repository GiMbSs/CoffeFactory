"""
Sales views for coffee_factory project.
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
from decimal import Decimal

from .models import Customer, SalesOrder, SalesOrderItem
from .forms import (
    CustomerForm, SalesOrderForm, SalesOrderItemForm, SalesOrderStatusUpdateForm,
    SalesReportForm, CustomerCreditForm, BulkOrderStatusForm,
    CustomerSearchForm, SalesOrderSearchForm
)
from inventory.models import Product


class SalesDashboardView(LoginRequiredMixin, TemplateView):
    """Sales dashboard view."""
    template_name = 'sales/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get sales statistics
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        this_week_start = today - timedelta(days=today.weekday())
        
        # Today's sales
        today_sales = SalesOrder.objects.filter(
            order_date=today,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        today_orders = SalesOrder.objects.filter(order_date=today).count()
        
        # Monthly sales
        monthly_sales = SalesOrder.objects.filter(
            order_date__gte=this_month_start,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        monthly_orders = SalesOrder.objects.filter(
            order_date__gte=this_month_start
        ).count()
        
        # Pending orders
        pending_orders = SalesOrder.objects.filter(status='pending').count()
        
        # Active customers
        active_customers = Customer.objects.filter(is_active=True).count()
        
        # Recent orders
        recent_orders = SalesOrder.objects.select_related('customer').order_by('-created_at')[:10]
        
        context['metrics'] = {
            'today_sales': today_sales,
            'today_orders': today_orders,
            'month_sales': monthly_sales,
            'month_orders': monthly_orders,
            'pending_orders': pending_orders,
            'active_customers': active_customers,
        }
        
        context['recent_orders'] = recent_orders
        
        # Legacy stats for backward compatibility
        context['stats'] = {
            'total_orders': SalesOrder.objects.count(),
            'orders_today': today_orders,
            'active_customers': active_customers,
            'total_revenue': SalesOrder.objects.filter(
                status='completed'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0'),
            'monthly_revenue': monthly_sales,
        }
        
        return context


class SalesOrderListView(LoginRequiredMixin, ListView):
    """Sales order list view."""
    model = SalesOrder
    template_name = 'sales/sales_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SalesOrder.objects.select_related(
            'customer'
        ).prefetch_related('order_items', 'order_items__product').all()
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__document__icontains=search) |
                Q(items__product__name__icontains=search)
            ).distinct()
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Customer filter
        customer = self.request.GET.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        # Date range filter
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        # Ordering
        ordering = self.request.GET.get('ordering', '-order_date')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter options
        context['customers'] = Customer.objects.filter(is_active=True)
        
        # Get statistics for current queryset
        queryset = self.get_queryset()
        context['stats'] = {
            'total_orders': queryset.count(),
            'draft_orders': queryset.filter(status='draft').count(),
            'confirmed_orders': queryset.filter(status='confirmed').count(),
            'delivered_orders': queryset.filter(status='delivered').count(),
            'total_value': queryset.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0'),
            'pending_payment': queryset.filter(
                status__in=['confirmed', 'in_production', 'ready', 'delivered']
            ).exclude(status='paid').count(),
            'pending_delivery': queryset.filter(
                status__in=['confirmed', 'in_production', 'ready']
            ).count(),
        }
        
        return context


class SalesOrderDetailView(LoginRequiredMixin, DetailView):
    """Sales order detail view."""
    model = SalesOrder
    template_name = 'sales/sales_order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Get order items with products
        context['order_items'] = order.items.select_related('product').all()
        
        # Calculate order totals
        context['subtotal'] = sum(item.total_price for item in context['order_items'])
        
        return context


class CustomerListView(LoginRequiredMixin, ListView):
    """Customer list view."""
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Customer.objects.all()
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(document__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Customer type filter
        customer_type = self.request.GET.get('customer_type')
        if customer_type:
            queryset = queryset.filter(customer_type=customer_type)
        
        # Active filter
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        # Ordering
        ordering = self.request.GET.get('ordering', 'name')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics
        queryset = self.get_queryset()
        context['stats'] = {
            'total_customers': queryset.count(),
            'active_customers': queryset.filter(is_active=True).count(),
            'pf_customers': queryset.filter(customer_type='pf').count(),
            'pj_customers': queryset.filter(customer_type='pj').count(),
        }
        
        return context


# AJAX Views
class SalesOrderStatusUpdateView(LoginRequiredMixin, TemplateView):
    """AJAX view to update sales order status."""
    
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        try:
            order = SalesOrder.objects.get(id=order_id)
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status atualizado para {order.get_status_display()}'
            })
        
        except SalesOrder.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Pedido não encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar status: {str(e)}'
            })
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    
    def get_queryset(self):
        return []


class SalesOrderCreateView(LoginRequiredMixin, CreateView):
    """Sales order create view."""
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'sales/sales_order_form.html'
    success_url = reverse_lazy('sales:sales_order_list')


class SalesOrderUpdateView(LoginRequiredMixin, UpdateView):
    """Sales order update view."""
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'sales/sales_order_form.html'
    success_url = reverse_lazy('sales:sales_order_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Pedido "{form.instance.order_number}" atualizado com sucesso!')
        return super().form_valid(form)


class CustomerCreateView(LoginRequiredMixin, CreateView):
    """Customer create view."""
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.name}" criado com sucesso!')
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    """Customer update view."""
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.name}" atualizado com sucesso!')
        return super().form_valid(form)


class CustomerDetailView(LoginRequiredMixin, DetailView):
    """Customer detail view."""
    model = Customer
    template_name = 'sales/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Get customer orders
        context['recent_orders'] = customer.sales_orders.all()[:10]
        context['total_orders'] = customer.sales_orders.count()
        context['total_revenue'] = customer.sales_orders.filter(
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        return context


class SalesReportsView(LoginRequiredMixin, TemplateView):
    """Sales reports view."""
    template_name = 'sales/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SalesReportForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = SalesReportForm(request.POST)
        if form.is_valid():
            # Process report generation here
            messages.success(request, 'Relatório gerado com sucesso!')
        return self.render_to_response({'form': form})


class CustomerCreditView(LoginRequiredMixin, TemplateView):
    """Customer credit management view."""
    template_name = 'sales/customer_credit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomerCreditForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CustomerCreditForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data['customer']
            new_limit = form.cleaned_data['new_credit_limit']
            reason = form.cleaned_data['reason']
            
            old_limit = customer.credit_limit
            customer.credit_limit = new_limit
            customer.save()
            
            messages.success(
                request, 
                f'Limite de crédito do cliente "{customer.name}" alterado de '
                f'R$ {old_limit} para R$ {new_limit}. Motivo: {reason}'
            )
            return redirect('sales:customer_detail', pk=customer.pk)
        
        return self.render_to_response({'form': form})


class BulkOrderStatusView(LoginRequiredMixin, TemplateView):
    """Bulk order status update view."""
    template_name = 'sales/bulk_order_status.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BulkOrderStatusForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = BulkOrderStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['new_status']
            order_ids = form.cleaned_data['selected_orders']
            notes = form.cleaned_data.get('notes', '')
            
            # Update orders
            updated_count = SalesOrder.objects.filter(
                id__in=order_ids
            ).update(status=new_status)
            
            messages.success(
                request, 
                f'{updated_count} pedidos atualizados para status "{new_status}"'
            )
            return redirect('sales:order_list')
        
        return self.render_to_response({'form': form})


class SalesOrderStatusUpdateView(LoginRequiredMixin, UpdateView):
    """Sales order status update view."""
    model = SalesOrder
    form_class = SalesOrderStatusUpdateForm
    template_name = 'sales/order_status_form.html'
    
    def get_success_url(self):
        return reverse_lazy('sales:order_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Status do pedido atualizado com sucesso!')
        return super().form_valid(form)
    model = Customer
    template_name = 'sales/customer_detail.html'
    context_object_name = 'customer'
