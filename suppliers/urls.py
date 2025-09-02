"""
Suppliers app URLs.
"""
from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.SuppliersListView.as_view(), name='list'),
    path('create/', views.SupplierCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.SupplierDetailView.as_view(), name='detail'),
    path('<uuid:pk>/update/', views.SupplierUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.SupplierDeleteView.as_view(), name='delete'),
    path('import/', views.SupplierImportView.as_view(), name='import'),
    path('report/', views.SuppliersReportView.as_view(), name='report'),
]
