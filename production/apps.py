from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """Configuration for the production app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production'
    verbose_name = 'Production Management'
