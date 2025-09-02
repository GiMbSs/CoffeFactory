"""
Test base classes and utilities for coffee_factory project.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication utilities."""
    
    def setUp(self):
        """Set up test fixtures for API tests."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create tokens for API authentication
        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin_user)
    
    def authenticate_user(self):
        """Authenticate as regular user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
    
    def authenticate_admin(self):
        """Authenticate as admin user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
    
    def unauthenticate(self):
        """Remove authentication."""
        self.client.credentials()
