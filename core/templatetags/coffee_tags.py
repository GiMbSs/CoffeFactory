"""
Custom template tags for the Coffee Factory Management System.
These tags help in dynamizing hardcoded data in templates.
"""
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse, NoReverseMatch
import json

register = template.Library()


@register.simple_tag
def system_config(key, default=None):
    """Get system configuration value."""
    from core.system_config import SystemConfig
    
    config_methods = {
        'monthly_sales_goal': SystemConfig.get_monthly_sales_goal,
        'max_materials_capacity': SystemConfig.get_max_materials_capacity,
        'max_products_capacity': SystemConfig.get_max_products_capacity,
        'storage_capacity_limit': SystemConfig.get_storage_capacity_limit,
        'low_stock_threshold': SystemConfig.get_low_stock_threshold,
    }
    
    if key in config_methods:
        return config_methods[key]()
    return default


@register.simple_tag
def safe_url(url_name, *args, **kwargs):
    """Safely get URL, return # if URL pattern doesn't exist."""
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#'


@register.filter
def to_json(value):
    """Convert Python object to JSON for use in JavaScript."""
    return mark_safe(json.dumps(value))


@register.inclusion_tag('partials/_progress_bar.html')
def progress_bar(current, maximum, color='primary', show_percentage=True):
    """Render a dynamic progress bar."""
    try:
        # Convert to float to handle string inputs
        current = float(current) if current else 0
        maximum = float(maximum) if maximum else 1
        
        if maximum > 0:
            percentage = min((current / maximum) * 100, 100)
        else:
            percentage = 0
    except (ValueError, TypeError):
        # If conversion fails, default to 0
        percentage = 0
        current = 0
        maximum = 1
    
    colors = {
        'primary': 'bg-blue-500',
        'success': 'bg-green-500',
        'warning': 'bg-yellow-500',
        'danger': 'bg-red-500',
        'coffee': 'bg-coffee-500',
    }
    
    return {
        'current': current,
        'maximum': maximum,
        'percentage': percentage,
        'color_class': colors.get(color, colors['primary']),
        'show_percentage': show_percentage,
    }


@register.inclusion_tag('partials/_dynamic_chart.html')
def dynamic_chart(chart_id, chart_type, labels, data, options=None):
    """Render a dynamic chart with Chart.js."""
    chart_options = options or {}
    
    return {
        'chart_id': chart_id,
        'chart_type': chart_type,
        'labels': labels,
        'data': data,
        'options': chart_options,
    }


@register.simple_tag
def percentage_of(value, total):
    """Calculate percentage of value in total."""
    if total > 0:
        return min((value / total) * 100, 100)
    return 0


@register.filter
def default_if_none_or_zero(value, default):
    """Return default if value is None or 0."""
    if value is None or value == 0:
        return default
    return value


@register.simple_tag(takes_context=True)
def breadcrumb_item(context, name, url_name=None, *args, **kwargs):
    """Add an item to breadcrumbs context."""
    if 'breadcrumbs' not in context:
        context['breadcrumbs'] = []
    
    url = None
    if url_name:
        try:
            url = reverse(url_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            url = None
    
    context['breadcrumbs'].append({
        'name': name,
        'url': url,
    })
    
    return ''


@register.simple_tag
def color_by_status(status, type='text'):
    """Return appropriate color class based on status."""
    status_colors = {
        'active': {'text': 'text-green-600', 'bg': 'bg-green-100', 'border': 'border-green-200'},
        'inactive': {'text': 'text-red-600', 'bg': 'bg-red-100', 'border': 'border-red-200'},
        'pending': {'text': 'text-yellow-600', 'bg': 'bg-yellow-100', 'border': 'border-yellow-200'},
        'completed': {'text': 'text-blue-600', 'bg': 'bg-blue-100', 'border': 'border-blue-200'},
        'cancelled': {'text': 'text-gray-600', 'bg': 'bg-gray-100', 'border': 'border-gray-200'},
        'in_progress': {'text': 'text-purple-600', 'bg': 'bg-purple-100', 'border': 'border-purple-200'},
    }
    
    return status_colors.get(status, status_colors['pending']).get(type, '')


@register.simple_tag
def format_currency(value, currency='BRL'):
    """Format currency value."""
    if value is None:
        return 'R$ 0,00'
    
    if currency == 'BRL':
        return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return f'{value:,.2f}'
