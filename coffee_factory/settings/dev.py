"""
Development settings for coffee_factory project.
"""

from .base import *
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development database - SQLite for quick setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Development CORS - allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar for development
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Debug toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# Additional logging for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Development static files
STATICFILES_DIRS += [
    BASE_DIR / 'static_dev',
]
