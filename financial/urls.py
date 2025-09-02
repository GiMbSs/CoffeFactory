"""
Financial app URLs.
"""
from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.FinancialDashboardView.as_view(), name='dashboard'),
    path('accounts-payable/', views.AccountsPayableListView.as_view(), name='accounts_payable'),
    path('accounts-receivable/', views.AccountsReceivableListView.as_view(), name='accounts_receivable'),
    path('payroll/', views.PayrollListView.as_view(), name='payroll'),
]
