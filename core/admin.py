from django.contrib import admin
from .models import BaseModel, TimestampedModel, AuditModel

# Note: BaseModel, TimestampedModel, and AuditModel are abstract models
# and should not be registered directly in admin.
# They are used as base classes for other models.

# If you have any concrete models in the core app, register them here.
# Example:
# @admin.register(YourConcreteModel)
# class YourConcreteModelAdmin(admin.ModelAdmin):
#     pass
