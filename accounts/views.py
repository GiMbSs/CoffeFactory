"""
Account views for coffee_factory project.
"""
from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.views import View

from .models import User, Employee
from .forms import (
    CustomAuthenticationForm, CustomUserCreationForm, EmployeeForm,
    UserProfileForm, PasswordChangeForm
)


class LoginView(DjangoLoginView):
    """Custom login view."""
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after successful login."""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('core:dashboard')


class LogoutView(View):
    """Custom logout view that handles both GET and POST."""
    template_name = 'accounts/logout.html'
    
    def get(self, request):
        """Handle GET request - show logout confirmation page."""
        # If user is authenticated, logout and show the page
        if request.user.is_authenticated:
            logout(request)
        return render(request, self.template_name)
    
    def post(self, request):
        """Handle POST request - logout and show confirmation page."""
        logout(request)
        return render(request, self.template_name)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""
    template_name = 'accounts/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """User profile update view."""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    """Password change view."""
    template_name = 'accounts/password_change.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PasswordChangeForm(self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('accounts:profile')
        else:
            return self.render_to_response({'form': form})


class UserRegistrationView(CreateView):
    """User registration view."""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return super().form_valid(form)


class EmployeeListView(LoginRequiredMixin, ListView):
    """Employee list view."""
    model = Employee
    template_name = 'accounts/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('user').all()
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(position__icontains=search)
            )
        
        # Department filter
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Active filter
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('user__first_name')


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Employee detail view."""
    model = Employee
    template_name = 'accounts/employee_detail.html'
    context_object_name = 'employee'


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """Employee creation view."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'accounts/employee_form.html'
    success_url = reverse_lazy('accounts:employee_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Now the user has been created and associated
        messages.success(self.request, f'Funcionário "{form.instance.user.get_full_name()}" criado com sucesso!')
        return response


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    """Employee update view."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'accounts/employee_form.html'
    success_url = reverse_lazy('accounts:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Funcionário "{form.instance.user.get_full_name()}" atualizado com sucesso!')
        return super().form_valid(form)


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    """Employee deletion view."""
    model = Employee
    template_name = 'accounts/employee_confirm_delete.html'
    success_url = reverse_lazy('accounts:employee_list')
    
    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        # Deactivate instead of deleting
        employee.is_active = False
        employee.user.is_active = False
        employee.save()
        employee.user.save()
        messages.success(request, f'Funcionário "{employee.user.get_full_name()}" desativado com sucesso!')
        return redirect(self.success_url)
