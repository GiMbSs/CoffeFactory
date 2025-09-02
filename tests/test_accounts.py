"""
Test user model and employee functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Employee
from tests.base import BaseTestCase

User = get_user_model()


class UserModelTest(BaseTestCase):
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test user creation with UUID primary key."""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='password123'
        )
        
        self.assertIsNotNone(user.id)
        self.assertTrue(isinstance(user.id, type(user.id)))  # UUID type
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertFalse(user.is_employee)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        expected = "John Doe (test2@example.com)"
        self.assertEqual(str(user), expected)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.assertEqual(user.get_full_name(), 'Jane Smith')
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            first_name='Bob'
        )
        
        self.assertEqual(user.get_short_name(), 'Bob')


class EmployeeModelTest(BaseTestCase):
    """Test Employee model functionality."""
    
    def test_employee_creation(self):
        """Test employee creation."""
        employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            department='production',
            position='Operador de Máquina',
            employment_type='full_time',
            hire_date='2024-01-15',
            salary=3500.00
        )
        
        self.assertIsNotNone(employee.id)
        self.assertEqual(employee.employee_id, 'EMP001')
        self.assertEqual(employee.department, 'production')
        self.assertTrue(employee.user.is_employee)
    
    def test_employee_str_representation(self):
        """Test employee string representation."""
        employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP002',
            department='sales',
            position='Vendedor',
            employment_type='full_time',
            hire_date='2024-02-01',
            salary=4000.00
        )
        
        expected = f"EMP002 - {self.user.get_full_name()} (sales)"
        self.assertEqual(str(employee), expected)
    
    def test_employee_save_marks_user_as_employee(self):
        """Test that saving employee marks user as employee."""
        self.assertFalse(self.user.is_employee)
        
        Employee.objects.create(
            user=self.user,
            employee_id='EMP003',
            department='admin',
            position='Assistente Administrativo',
            employment_type='part_time',
            hire_date='2024-03-01',
            salary=2500.00
        )
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_employee)
