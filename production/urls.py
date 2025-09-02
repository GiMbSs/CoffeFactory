"""
Production app URLs.
"""
from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    # Dashboard
    path('', views.ProductionDashboardView.as_view(), name='dashboard'),
    
    # Production Orders
    path('orders/', views.ProductionOrderListView.as_view(), name='production_order_list'),
    path('orders/new/', views.ProductionOrderCreateView.as_view(), name='production_order_create'),
    path('orders/<uuid:pk>/', views.ProductionOrderDetailView.as_view(), name='production_order_detail'),
    path('orders/<uuid:pk>/edit/', views.ProductionOrderUpdateView.as_view(), name='production_order_update'),
    
    # Recipes
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipes/new/', views.RecipeCreateView.as_view(), name='recipe_create'),
    path('recipes/<uuid:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    
    # AJAX endpoints
    path('api/orders/status-update/', views.ProductionOrderStatusUpdateView.as_view(), name='production_order_status_update'),
]
