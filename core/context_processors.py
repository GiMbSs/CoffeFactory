"""
Context processors for coffee_factory project.
Provides global template context data.
"""
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .system_config import SystemConfig


def global_context(request):
    """
    Provide global context data for templates.
    """
    context = {}
    
    # Add system configuration to context
    context.update({
        'system_config': SystemConfig,
        'company_info': SystemConfig.get_company_info(),
        'chart_defaults': SystemConfig.get_chart_defaults(),
    })
    
    # Only process for authenticated users
    if request.user.is_authenticated:
        try:
            from inventory.models import Product
            from financial.models import AccountsPayable
            from django.db.models import Q
            import datetime
            
            # Notification system
            notifications = []
            
            # Stock alerts - Using dynamic threshold
            low_stock_threshold = SystemConfig.get_low_stock_threshold()
            products_with_stock = []
            for product in Product.objects.all():
                if product.current_stock <= product.minimum_stock or product.current_stock <= low_stock_threshold:
                    products_with_stock.append(product)
            products_low_stock = len(products_with_stock)
            
            if products_low_stock > 0:
                notifications.append({
                    'type': 'warning',
                    'title': 'Estoque Baixo',
                    'message': f'{products_low_stock} produtos com estoque abaixo do mínimo',
                    'url': 'inventory:product_list',
                    'icon': 'fas fa-exclamation-triangle'
                })
            
            # Pending payments
            today = timezone.now().date()
            due_payments = AccountsPayable.objects.filter(
                due_date__lte=today + datetime.timedelta(days=3),
                status='pending'
            ).count()
            
            if due_payments > 0:
                notifications.append({
                    'type': 'info',
                    'title': 'Vencimentos Próximos',
                    'message': f'{due_payments} contas a pagar vencem em 3 dias',
                    'url': 'financial:accounts_payable',
                    'icon': 'fas fa-clock'
                })
            
            context.update({
                'notifications': notifications,
                'notification_count': len(notifications),
            })
            
        except Exception as e:
            # Handle any database or import errors gracefully
            context.update({
                'notifications': [],
                'notification_count': 0,
            })
    
    return context
