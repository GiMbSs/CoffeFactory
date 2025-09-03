"""
Sales app URLs.
"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Dashboard
    path('', views.SalesDashboardView.as_view(), name='dashboard'),
    
    # Sales Orders
    path('orders/', views.SalesOrderListView.as_view(), name='sales_order_list'),
    path('orders/new/', views.SalesOrderCreateView.as_view(), name='sales_order_create'),
    path('orders/<uuid:pk>/', views.SalesOrderDetailView.as_view(), name='sales_order_detail'),
    path('orders/<uuid:pk>/edit/', views.SalesOrderUpdateView.as_view(), name='sales_order_edit'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/new/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<uuid:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<uuid:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    
    # Reports
    path('reports/', views.SalesReportsView.as_view(), name='reports'),
    
    # AJAX endpoints
    path('api/orders/status-update/', views.SalesOrderStatusUpdateView.as_view(), name='sales_order_status_update'),
]
