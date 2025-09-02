"""
Accounts app URLs.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<uuid:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
]
