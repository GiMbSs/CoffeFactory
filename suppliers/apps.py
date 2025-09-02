from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    """Configuration for the suppliers app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suppliers'
    verbose_name = 'Supplier Management'
