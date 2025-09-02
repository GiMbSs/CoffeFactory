"""
URL Configuration for Coffee Factory API

This module defines the URL patterns for the Coffee Factory Management
System API endpoints. Uses Django REST Framework routers for automatic
URL pattern generation and API documentation.

API Structure:
- /api/v1/ - Main API endpoint
- /api/v1/docs/ - Swagger/OpenAPI documentation
- /api/v1/redoc/ - ReDoc documentation
- Standard CRUD endpoints for all models with custom actions
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

from .views import (
    # Employee & User ViewSets
    EmployeeViewSet,
    
    # Inventory ViewSets
    CategoryViewSet,
    MaterialViewSet,
    ProductViewSet,
    StockMovementViewSet,
    
    # Supplier ViewSets
    SupplierViewSet,
    
    # Production ViewSets
    RecipeViewSet,
    ProductionOrderViewSet,
    
    # Sales ViewSets
    CustomerViewSet,
    SalesOrderViewSet,
    SalesOrderItemViewSet,
    
    # Financial ViewSets
    AccountsPayableViewSet,
    AccountsReceivableViewSet,
    PayrollViewSet,
)

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()

# Employee & User endpoints
router.register(r'employees', EmployeeViewSet, basename='employee')

# Inventory endpoints
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')

# Supplier endpoints
router.register(r'suppliers', SupplierViewSet, basename='supplier')

# Production endpoints
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'production-orders', ProductionOrderViewSet, basename='productionorder')

# Sales endpoints
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'sales-orders', SalesOrderViewSet, basename='salesorder')
router.register(r'sales-order-items', SalesOrderItemViewSet, basename='salesorderitem')

# Financial endpoints
router.register(r'accounts-payable', AccountsPayableViewSet, basename='accountspayable')
router.register(r'accounts-receivable', AccountsReceivableViewSet, basename='accountsreceivable')
router.register(r'payroll', PayrollViewSet, basename='payroll')

urlpatterns = [
    # API Documentation  
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
    
    # API Endpoints - Include router URLs directly
    path('', include(router.urls)),
    
    # Authentication endpoints (if using token auth)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
