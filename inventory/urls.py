"""
Inventory app URLs.
"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.InventoryDashboardView.as_view(), name='dashboard'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<uuid:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<uuid:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Materials
    path('materials/', views.MaterialListView.as_view(), name='material_list'),
    path('materials/new/', views.MaterialCreateView.as_view(), name='material_create'),
    path('materials/<uuid:pk>/', views.MaterialDetailView.as_view(), name='material_detail'),
    path('materials/<uuid:pk>/edit/', views.MaterialUpdateView.as_view(), name='material_update'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<uuid:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    
    # Stock Movements
    path('stock-movements/new/', views.StockMovementCreateView.as_view(), name='stock_movement_create'),
    
    # AJAX endpoints
    path('api/materials/stock-status/', views.MaterialStockStatusView.as_view(), name='material_stock_status'),
    path('api/stats/', views.InventoryStatsView.as_view(), name='inventory_stats'),
]
