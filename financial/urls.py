"""
Financial app URLs.
"""
from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.FinancialDashboardView.as_view(), name='dashboard'),
    
    # Accounts Payable URLs
    path('accounts-payable/', views.AccountsPayableListView.as_view(), name='accounts_payable'),
    path('accounts-payable/create/', views.AccountsPayableCreateView.as_view(), name='accounts_payable_create'),
    
    # Accounts Receivable URLs
    path('accounts-receivable/', views.AccountsReceivableListView.as_view(), name='accounts_receivable'),
    path('accounts-receivable/create/', views.AccountsReceivableCreateView.as_view(), name='accounts_receivable_create'),
    
    # Payroll URLs
    path('payroll/', views.PayrollListView.as_view(), name='payroll'),
    
    # Reports
    path('reports/', views.FinancialReportsView.as_view(), name='reports'),
]
