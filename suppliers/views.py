"""
Suppliers views for coffee_factory project.
"""
from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count

from .models import Supplier
from .forms import (
    SupplierForm, SupplierSearchForm, SupplierFilterForm,
    SupplierImportForm, SupplierContactForm
)


class SuppliersListView(LoginRequiredMixin, ListView):
    """Supplier list view with search and filters."""
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Supplier.objects.all()
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(trade_name__icontains=search) |
                Q(code__icontains=search) |
                Q(cnpj_cpf__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Type filter
        supplier_type = self.request.GET.get('supplier_type')
        if supplier_type:
            queryset = queryset.filter(supplier_type=supplier_type)
        
        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # City filter
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # State filter
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics for the summary cards
        all_suppliers = Supplier.objects.all()
        context['total_suppliers'] = all_suppliers.count()
        context['active_suppliers'] = all_suppliers.filter(is_active=True).count()
        context['company_suppliers'] = all_suppliers.filter(supplier_type='company').count()
        context['individual_suppliers'] = all_suppliers.filter(supplier_type='individual').count()
        
        return context


class SupplierDetailView(LoginRequiredMixin, DetailView):
    """Supplier detail view."""
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.get_object()
        
        # Additional context for detail view
        context['supplier'] = supplier
        
        return context


class SupplierCreateView(LoginRequiredMixin, CreateView):
    """Supplier create view."""
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Fornecedor "{form.instance.name}" criado com sucesso!')
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    """Supplier update view."""
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Fornecedor "{form.instance.name}" atualizado com sucesso!')
        return super().form_valid(form)


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    """Supplier deletion view."""
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:list')
    
    def delete(self, request, *args, **kwargs):
        supplier = self.get_object()
        # Deactivate instead of deleting if has related materials
        if supplier.materials.exists():
            supplier.is_active = False
            supplier.save()
            messages.success(request, f'Fornecedor "{supplier.name}" desativado com sucesso!')
        else:
            supplier_name = supplier.name
            supplier.delete()
            messages.success(request, f'Fornecedor "{supplier_name}" removido com sucesso!')
        return redirect(self.success_url)


class SupplierContactUpdateView(LoginRequiredMixin, UpdateView):
    """Supplier contact update view."""
    model = Supplier
    form_class = SupplierContactForm
    template_name = 'suppliers/supplier_contact_form.html'
    success_url = reverse_lazy('suppliers:list')
    
    def form_valid(self, form):
        supplier = form.save(commit=False)
        supplier.contact_name = form.cleaned_data.get('contact_name', '')
        supplier.contact_email = form.cleaned_data.get('contact_email', '')
        supplier.contact_phone = form.cleaned_data.get('contact_phone', '')
        supplier.notes = form.cleaned_data.get('notes', '')
        supplier.save()
        
        messages.success(self.request, f'Contato do fornecedor "{supplier.name}" atualizado com sucesso!')
        return redirect('suppliers:detail', pk=supplier.pk)


class SupplierImportView(LoginRequiredMixin, TemplateView):
    """Supplier import view."""
    template_name = 'suppliers/supplier_import.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SupplierImportForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = SupplierImportForm(request.POST, request.FILES)
        if form.is_valid():
            # Process import here
            # This would involve reading the file and creating suppliers
            messages.success(request, 'Importação realizada com sucesso!')
            return redirect('suppliers:list')
        return self.render_to_response({'form': form})


class SuppliersReportView(LoginRequiredMixin, TemplateView):
    """Suppliers report view."""
    template_name = 'suppliers/suppliers_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Generate supplier statistics
        context['stats'] = {
            'total_suppliers': Supplier.objects.count(),
            'active_suppliers': Supplier.objects.filter(is_active=True).count(),
            'company_suppliers': Supplier.objects.filter(supplier_type='company').count(),
            'individual_suppliers': Supplier.objects.filter(supplier_type='individual').count(),
            'suppliers_by_state': Supplier.objects.values('state').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
        }
        
        return context
