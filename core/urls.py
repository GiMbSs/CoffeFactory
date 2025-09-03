"""
Core app URLs.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('documentation/', views.DocumentationView.as_view(), name='documentation'),
]
