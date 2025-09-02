"""
Financial views for coffee_factory project.
"""
from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal

from .models import (
    AccountsReceivable, AccountsReceivablePayment, 
    AccountsPayable, AccountsPayablePayment, Payroll
)
from .forms import (
    AccountsReceivableForm, AccountsPayableForm, FinancialReportForm
)


class FinancialDashboardView(LoginRequiredMixin, TemplateView):
    """Financial dashboard view."""
    template_name = 'financial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get financial statistics
        context['stats'] = {
            'total_receivables': AccountsReceivable.objects.filter(status='pending').count(),
            'total_payables': AccountsPayable.objects.filter(status='pending').count(),
        }
        
        return context


# Accounts Receivable Views
class AccountsReceivableListView(LoginRequiredMixin, ListView):
    """Accounts receivable list view."""
    model = AccountsReceivable
    template_name = 'financial/accounts_receivable.html'
    context_object_name = 'receivables'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate summary statistics
        receivables = AccountsReceivable.objects.all()
        
        context['total_amount'] = sum(r.original_amount for r in receivables) if receivables else 0
        context['total_paid'] = sum(r.paid_amount for r in receivables) if receivables else 0
        context['total_pending'] = sum(r.balance for r in receivables) if receivables else 0
        context['overdue_amount'] = sum(r.balance for r in receivables.filter(status='overdue')) if receivables else 0
        context['overdue_count'] = receivables.filter(status='overdue').count()
        
        # Due today
        from datetime import date
        due_today = receivables.filter(due_date=date.today(), status__in=['pending', 'partially_paid'])
        context['due_today_amount'] = sum(r.balance for r in due_today) if due_today else 0
        context['due_today_count'] = due_today.count()
        
        return context


class AccountsReceivableCreateView(LoginRequiredMixin, CreateView):
    """Accounts receivable creation view."""
    model = AccountsReceivable
    form_class = AccountsReceivableForm
    template_name = 'financial/accounts_receivable_form.html'
    success_url = reverse_lazy('financial:accounts_receivable')
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta a receber criada com sucesso!')
        return super().form_valid(form)


# Accounts Payable Views
class AccountsPayableListView(LoginRequiredMixin, ListView):
    """Accounts payable list view."""
    model = AccountsPayable
    template_name = 'financial/accounts_payable.html'
    context_object_name = 'payables'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate summary statistics
        payables = AccountsPayable.objects.all()
        
        context['total_amount'] = sum(p.original_amount for p in payables) if payables else 0
        context['total_paid'] = sum(p.paid_amount for p in payables) if payables else 0
        context['total_pending'] = sum(p.balance for p in payables) if payables else 0
        context['overdue_amount'] = sum(p.balance for p in payables.filter(status='overdue')) if payables else 0
        context['overdue_count'] = payables.filter(status='overdue').count()
        
        # Due today
        from datetime import date
        due_today = payables.filter(due_date=date.today(), status__in=['pending', 'partially_paid'])
        context['due_today_amount'] = sum(p.balance for p in due_today) if due_today else 0
        context['due_today_count'] = due_today.count()
        
        return context


class AccountsPayableCreateView(LoginRequiredMixin, CreateView):
    """Accounts payable creation view."""
    model = AccountsPayable
    form_class = AccountsPayableForm
    template_name = 'financial/accounts_payable_form.html'
    success_url = reverse_lazy('financial:accounts_payable')
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta a pagar criada com sucesso!')
        return super().form_valid(form)


# Payroll Views
class PayrollListView(LoginRequiredMixin, ListView):
    """Payroll list view."""
    model = Payroll
    template_name = 'financial/payroll.html'
    context_object_name = 'payrolls'
    paginate_by = 20


# Reports Views
class FinancialReportsView(LoginRequiredMixin, TemplateView):
    """Financial reports view."""
    template_name = 'financial/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FinancialReportForm()
        return context
