"""
System configuration for Coffee Factory Management System.
This module provides dynamic configuration values that can be used
instead of hardcoded values throughout the application.
"""
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache


class SystemConfig:
    """System configuration manager."""
    
    # Cache timeout for configuration values (1 hour)
    CACHE_TIMEOUT = 3600
    
    @classmethod
    def get_monthly_sales_goal(cls):
        """Get monthly sales goal from cache or default."""
        key = 'monthly_sales_goal'
        value = cache.get(key)
        if value is None:
            value = getattr(settings, 'MONTHLY_SALES_GOAL', Decimal('100000'))
            cache.set(key, value, cls.CACHE_TIMEOUT)
        return value
    
    @classmethod
    def get_max_materials_capacity(cls):
        """Get maximum materials capacity."""
        key = 'max_materials_capacity'
        value = cache.get(key)
        if value is None:
            value = getattr(settings, 'MAX_MATERIALS_CAPACITY', 100)
            cache.set(key, value, cls.CACHE_TIMEOUT)
        return value
    
    @classmethod
    def get_max_products_capacity(cls):
        """Get maximum products capacity."""
        key = 'max_products_capacity'
        value = cache.get(key)
        if value is None:
            value = getattr(settings, 'MAX_PRODUCTS_CAPACITY', 50)
            cache.set(key, value, cls.CACHE_TIMEOUT)
        return value
    
    @classmethod
    def get_storage_capacity_limit(cls):
        """Get storage capacity limit in percentage."""
        key = 'storage_capacity_limit'
        value = cache.get(key)
        if value is None:
            value = getattr(settings, 'STORAGE_CAPACITY_LIMIT', 85)
            cache.set(key, value, cls.CACHE_TIMEOUT)
        return value
    
    @classmethod
    def get_low_stock_threshold(cls):
        """Get low stock threshold."""
        key = 'low_stock_threshold'
        value = cache.get(key)
        if value is None:
            value = getattr(settings, 'LOW_STOCK_THRESHOLD', 10)
            cache.set(key, value, cls.CACHE_TIMEOUT)
        return value
    
    @classmethod
    def get_company_info(cls):
        """Get company information."""
        return {
            'name': getattr(settings, 'COMPANY_NAME', 'Coffee Factory'),
            'tagline': getattr(settings, 'COMPANY_TAGLINE', 'Management System'),
            'email': getattr(settings, 'COMPANY_EMAIL', 'contato@coffeefactory.com'),
            'phone': getattr(settings, 'COMPANY_PHONE', '(11) 99999-9999'),
            'address': getattr(settings, 'COMPANY_ADDRESS', 'São Paulo, SP'),
        }
    
    @classmethod
    def get_chart_defaults(cls):
        """Get default chart configurations."""
        return {
            'sales_chart_months': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'production_categories': ['Café Espresso', 'Café Premium', 'Café Orgânico', 
                                    'Café Descafeinado', 'Café Especial'],
            'color_palette': {
                'primary': '#3b82f6',
                'success': '#10b981', 
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'info': '#8b5cf6'
            }
        }
    
    @classmethod
    def invalidate_cache(cls, key=None):
        """Invalidate configuration cache."""
        if key:
            cache.delete(key)
        else:
            # Clear all config cache keys
            keys = [
                'monthly_sales_goal', 'max_materials_capacity', 
                'max_products_capacity', 'storage_capacity_limit',
                'low_stock_threshold'
            ]
            cache.delete_many(keys)
