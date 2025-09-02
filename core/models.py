"""
Core models for coffee_factory project.
Base abstract models and common utilities.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamp fields.
    All models should inherit from this base model.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} ({self.id})"


class TimestampedModel(models.Model):
    """
    Abstract model providing timestamp fields only.
    For models that need their own primary key.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditModel(BaseModel):
    """
    Abstract model providing audit trail fields.
    Extends BaseModel with user tracking.
    """
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        null=True,
        blank=True,
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        null=True,
        blank=True,
        help_text="User who last updated this record"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to handle audit fields."""
        user = kwargs.pop('user', None)
        if user:
            if not self.pk:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)
