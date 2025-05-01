"""
This file contains test cases for user management functionalities 
The tests cover:
- Permissions: Ensuring that only admin users can access certain views.
- Managing users: Admins can retrieve the list of all users while non-admins are restricted.
- Adding users: Tests for successful user creation, handling duplicate emails, missing fields, and unauthenticated requests.
- Editing users: Tests for retrieving and updating user details, including invalid data and non-existent users.
- Deleting users: Tests for successful deletion, handling of non-existent users, and unauthenticated attempts.

"""

from django.test import TestCase
from rest_framework.test import APIClient, APITestCase, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from auth_app.models import users
from .serializers import StaffSerializer
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from .views import IsAdminUser
from django.core.exceptions import ValidationError

User = get_user_model()

class TestIsAdminUserPermission(TestCase):
    def setUp(self):
        self.permission = IsAdminUser()

        # Create a test admin and staff user
        self.admin_user = users.objects.create_user(
            first_name='Test',
            last_name='Admin',
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False,
            theme_preference='light'
        )

        self.regular_user = users.objects.create_user(
            first_name='Test',
            last_name='Staffer',
            username="staffer",
            password="staffpassword",
            email="staffer@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='staff',
            is_staff=True,
            theme_preference='light'
        )

        # Create an API client instance
        self.client = APIClient()

    # test_admin_user_has_permission(): Admin user has permission
    def test_admin_user_has_permission(self):
        # Act
        request = self.client.get('/')
        request.user = self.admin_user

        # Assert
        self.assertTrue(self.permission.has_permission(request, None))

    # test_regular_user_has_no_permission(): Regular user does not have permission
    def test_regular_user_has_no_permission(self):
        # Act
        request = self.client.get('/')
        request.user = self.regular_user

        # Assert
        self.assertFalse(self.permission.has_permission(request, None))

    # test_unauthenticated_user_has_no_permission(): Unauthenticated user does not have permission
    def test_unauthenticated_user_has_no_permission(self):
        # Act
        request = self.client.get('/')
        request.user = None

        # Assert
        self.assertFalse(self.permission.has_permission(request, None))

class ManageUsersViewTest(TestCase):
    # setUp(): Set up objects to be used in the tests
    def setUp(self):
        # Create a test admin and staff user
        self.admin_user = users.objects.create_user(
            first_name='Test',
            last_name='Admin',
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False,
            theme_preference='light'
        )

        self.staff_user = users.objects.create_user(
            first_name='Test',
            last_name='Employee',
            username="employee",
            password="employeepassword",
            email="employee@example.com",
            date_of_hire='2025-12-29',
            department='Testing',
            role='user',
            is_staff=True,
            theme_preference='light'
        )

        # Set up a URL for managing users
        self.manage_users_url = reverse('manage_users')

        # Create an API client instance
        self.client = APIClient()

    @patch('auth_app.models.users.objects.all')
    @patch('auth_app.serializers.StaffSerializer')
    # test_manage_users_authenticated_request(): Test the successful retrieval of user data for authenticated, admin users
    def test_manage_users_authenticated_request(self, mock_serializer, mock_users_all):
        # Arrange: Mock serializer and set up authentication
        mock_users_all.return_value = [self.admin_user]
        serialized_user = {
            "user_id": self.admin_user.user_id,
            "username": self.admin_user.username,
            "email": self.admin_user.email,
            "role": self.admin_user.role,
            "date_of_hire": self.admin_user.date_of_hire,
            "first_name": self.admin_user.first_name,
            "last_name": self.admin_user.last_name,
            "department": self.admin_user.department,
            "is_active": self.admin_user.is_active,
            "is_staff": self.admin_user.is_staff,
        }
        mock_serializer.return_value.data = [serialized_user]
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Act: Make GET request to manage users endpoint
        response = self.client.get(self.manage_users_url)

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,[serialized_user])
        mock_users_all.assert_called_once()

    # test_manage_users_non_admin_user_request(): Handling of a non-authorized role (not an admin)
    def test_manage_users_non_admin_user_request(self):
        # Arrange: Authenticate non-admin user
        refresh = RefreshToken.for_user(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Act: Make GET request to manage users endpoint
        response = self.client.get(self.manage_users_url)

        # Assert: Check if exception was raised and response status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # check if user was not authorized
        self.assertEqual(response.data, {'detail': 'You do not have permission to perform this action.'}) # checking that only data retrieved was the error message

    @patch('auth_app.models.users.objects.all')
    # test_manage_users_user_retrieval_failure(): Handling of an exception during user retrieval
    def test_manage_users_user_retrieval_failure(self, mock_objects_all):
        # Arrange: Mock user retrieval to raise an exception
        mock_objects_all.side_effect = Exception("Database error")
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Act: Make GET request to manage users endpoint
        response = self.client.get(self.manage_users_url)

        # Assert: Check if exception was raised and response status
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"error": "Database error"})

class AddUserTests(APITestCase):
    # setUp(): Set up objects to be used in the tests
    def setUp(self):
        # Create an admin user who will perform the add operations
        self.admin_user = users.objects.create_user(
            username='adminuser',
            email='adminuser@example.com',
            password='adminpassword',
            role='admin',
            date_of_hire='1980-08-08',
            first_name='Admin',
            last_name='User',
            department='Administration',
            is_staff=False,
            is_active=True,
        )

        # Valid user data to pass in POST request
        self.valid_user_data = {
            'username': 'validuser',
            'email': 'validuser@example.com',
            'password': 'userpassword',
            'role': 'user',
            'date_of_hire': '1980-08-08',
            'first_name': 'Valid',
            'last_name': 'User',
            'department': 'Userville',
            'is_staff': True,
            'is_active': True   
        }

        # Create a non-admin user for testing
        self.staff_user = users.objects.create_user(
            first_name='Test',
            last_name='Employee',
            username="employee",
            password="employeepassword",
            email="employee@example.com",
            date_of_hire='2025-12-29',
            department='Testing',
            role='user',
        )

        # Create an API client instance
        self.client = APIClient()

        # Set up the URL for adding users
        self.add_user_url = reverse('add_user')

    @patch('auth_app.models.users.objects.filter')
    # test_add_user_success(): Ensure that an authenticated, admin user can add a new user successfully
    def test_add_user_success(self, mock_filter):        
        # Arrange: Mock user creation and authenticate user
        mock_filter.return_value.exists.return_value = False
        with patch('auth_app.models.users.objects.create_user') as mock_create:
            refresh = RefreshToken.for_user(self.admin_user)
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
            
            # Act: Make POST request to add user endpoint
            response = self.client.post(
                self.add_user_url,
                data=self.valid_user_data,
                format='json'
            )
            
            # Assert: Check response status and data
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {"message": "User created successfully"})
            mock_create.assert_called_once_with(
                username='validuser',
                password='userpassword',
                email='validuser@example.com',
                role='user',
                first_name='Valid',
                last_name='User',
                department='Userville',
                date_of_hire='1980-08-08'
            )

    @patch('auth_app.models.users.objects.filter')
    # test_add_user_duplicate_email(): Ensure that adding a user with an existing email fails
    def test_add_user_duplicate_email(self, mock_filter):        
        # Arrange: Mock the users.objects.filter to return True (user exists) and authenticate user
        mock_filter.return_value.exists.return_value = True

        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Act: Make POST request to add user endpoint
        response = self.client.post(
            self.add_user_url,
            data=self.valid_user_data,
            format='json',
        )
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "User with this email already exists"})
        mock_filter.assert_called_once_with(email=self.valid_user_data['email'])

    # test_add_user_missing_fields(): Ensure that missing required fields result in a 500 error
    def test_add_user_missing_fields(self):
        # Arrange: Create incomplete user data and authenticate user
        incomplete_data = {
            'username': 'incompleteuser',
            # Missing password, email, and other required fields
        }
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Act: Make POST request to add user endpoint
        response = self.client.post(self.add_user_url, incomplete_data, format='json')

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    # test_add_user_unauthenticated(): Ensure that an unauthenticated user cannot add a new user
    def test_add_user_unauthenticated(self):
        # Act: Make POST request to add user endpoint without authentication
        response = self.client.post(
            self.add_user_url,
            data=self.valid_user_data,
            format='json',
        )
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    # test_add_user_non_admin_user(): Ensure that a non-admin user cannot add a new user.
    def test_add_user_non_admin_user(self):
        # Arrange: Authenticate non-admin user
        refresh = RefreshToken.for_user(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Act: Make POST request to add user endpoint
        response = self.client.post(
            self.add_user_url,
            data=self.valid_user_data,
            format='json'
        )

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

class EditUserTests(APITestCase):
    def setUp(self):
        # Create a user who will perform the edit operations
        self.editor_user = users.objects.create_user(
            username='editoruser',
            email='editoruser@example.com',
            password='editorpassword',
            role='admin',
            date_of_hire='1985-05-15',
            first_name='Editor',
            last_name='User',
            department='Editing',
            is_staff=True,
            is_active=True,
        )
        # Create a user who will be the target of edit operations
        self.target_user = users.objects.create_user(
            username='targetuser',
            email='targetuser@example.com',
            password='targetpassword',
            role='staff',
            date_of_hire='1990-01-01',
            first_name='Target',
            last_name='User',
            department='Targeting',
            is_active=True,
            is_staff=True,
        )
        # Create a regular user for testing
        self.regular_user = users.objects.create_user(
            username='staffuser',
            email='staffuser@example.com',
            password='staffpassword',
            role='user',
            date_of_hire='1990-01-01',
            first_name='Staff',
            last_name='User',
            department='Staffington',
        )

        # Create test data to pass in PUT request
        self.update_data = {             
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'department': 'UpdatedDepartment'
        }
        self.invalid_update_email = { 'email': 'invalid-email' }  # Invalid email format

        # Create an API client instance
        self.client = APIClient()

        # Set up the URLs for editing
        self.edit_user_url = reverse('edit_user', kwargs={'user_id': self.target_user.user_id})

    @patch('auth_app.models.users.objects.get')
    # test_get_user_success(): Ensure that an authenticated user can retrieve details of another user
    def test_get_user_success(self, mock_get):
        # Arrange: Mock user retrieval and staff serializer, and authenticate the editor user
        mock_get.return_value = self.target_user
        
        serializer_data = {
            "user_id": self.target_user.user_id,
            "username": self.target_user.username,
            "email": self.target_user.email,
            "role": self.target_user.role,
            "date_of_hire": self.target_user.date_of_hire,
            "first_name": self.target_user.first_name,
            "last_name": self.target_user.last_name,
            "department": self.target_user.department,
            "is_active": self.target_user.is_active,
            "is_staff": self.target_user.is_staff,
        }
        with patch('admin_dashboard.serializers.StaffSerializer') as mock_serializer:
            mock_serializer.return_value.data = serializer_data
            self.client.force_authenticate(user=self.editor_user)

            # Act: Make GET request to edit user endpoint
            response = self.client.get(self.edit_user_url)

            # Assert: Check response status and data
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['username'], serializer_data['username'])
            self.assertEqual(response.data['email'], serializer_data['email'])
            self.assertEqual(response.data['role'], serializer_data['role'])
            self.assertEqual(response.data['first_name'], serializer_data['first_name'])
            self.assertEqual(response.data['last_name'], serializer_data['last_name'])
            self.assertEqual(response.data['department'], serializer_data['department'])

    @patch('auth_app.models.users.objects.get')
    # test_get_user_not_found(): Ensure that requesting a non-existent user returns a 404 error
    def test_get_user_not_found(self, mock_get):
        # Arrange: Mock user retrieval to raise an exception, authenticate user, and set up URL
        mock_get.side_effect = users.DoesNotExist()
        self.client.force_authenticate(user=self.editor_user)
        url = reverse('edit_user', kwargs={'user_id': 9999})

        # Act: Make GET request to edit user endpoint
        response = self.client.get(url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')

    # test_get_user_unauthenticated(): Ensure that an unauthenticated user cannot retrieve user details
    def test_get_user_unauthenticated(self):
        # Act: Make GET request to edit user endpoint without authentication
        response = self.client.get(self.edit_user_url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # test_get_user_non_admin_user(): Ensure that a non-admin user cannot retrieve another user's details
    def test_get_user_non_admin_user(self):
        # Arrange: Authenticate the staff user
        self.client.force_authenticate(user=self.regular_user)

        # Act: Make GET request to edit user endpoint
        response = self.client.get(self.edit_user_url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    @patch('auth_app.models.users.objects.get')
    # test_get_user_server_error(): Ensure that an error during user retrieval returns a 500 error
    def test_get_user_server_error(self, mock_get):
        # Arrange: Mock user retrieval to raise an exception and authenticate user
        mock_get.side_effect = Exception("Database error")
        self.client.force_authenticate(user=self.editor_user)

        # Act: Make GET request to edit user endpoint
        response = self.client.get(self.edit_user_url)
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("An error occurred", response.data["error"])

    @patch('auth_app.models.users.objects.get')
    # test_update_user_success(): Ensure that an authenticated user can update another user's details
    def test_update_user_success(self, mock_get):
        # Arrange: Mock user retrieval and staff serializer, and authenticate the editor user
        mock_get.return_value = self.target_user
  
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        with patch('admin_dashboard.serializers.StaffSerializer', return_value=mock_serializer):
            self.client.force_authenticate(user=self.editor_user)
            
            # Act: Make PUT request to edit user endpoint
            response = self.client.put(self.edit_user_url, self.update_data, format='json')
            
            # Assert: Check response and database value
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {"message": "User updated successfully"})
            self.target_user.refresh_from_db()
            self.assertEqual(self.target_user.first_name, 'UpdatedFirstName')
            self.assertEqual(self.target_user.last_name, 'UpdatedLastName')
            self.assertEqual(self.target_user.department, 'UpdatedDepartment')

    @patch('auth_app.models.users.objects.get')
    # test_update_user_invalid_email(): Ensure that updating user with an invalid email returns a 400 error
    def test_update_user_invalid_email(self, mock_get):
        # Arrange: Mock user retrieval and staff serializer to simulate invalid email
        mock_get.return_value = self.target_user
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = False
        mock_serializer.errors = {'email': ['Enter a valid email address.']}

        with patch('admin_dashboard.serializers.StaffSerializer', return_value=mock_serializer):
            self.client.force_authenticate(user=self.editor_user)

            # Act: Make PUT request to edit user endpoint with invalid email
            response = self.client.put(self.edit_user_url, self.invalid_update_email, format='json')

            # Assert: Check if exception was raised
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data, 
                {'email': ['Enter a valid email address.']}
            )

    @patch('auth_app.models.users.objects.get')
    # test_update_user_not_found(): Ensure that updating a non-existent user returns a 404 error
    def test_update_user_not_found(self, mock_get):
        # Arrange: Mock user retrieval to raise an exception and authenticate user
        mock_get.side_effect = users.DoesNotExist()
        self.client.force_authenticate(user=self.editor_user)

        # Act: Make PUT request to edit user endpoint
        response = self.client.put(self.edit_user_url, self.update_data, format='json') 
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "User not found"})   

    @patch('auth_app.models.users.objects.get')
    # test_update_user_server_error(): Ensure that an error during user retrieval returns a 500 error
    def test_update_user_server_error(self, mock_get):
        # Arrange: Mock user retrieval to raise an exception and authenticate user
        mock_get.side_effect = Exception("Database error")
        self.client.force_authenticate(user=self.editor_user)

        # Act: Make PUT request to edit user endpoint
        response = self.client.put(self.edit_user_url, self.update_data, format='json')
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "An error occurred: Database error")

    # test_update_user_unauthenticated(): Ensure that an unauthenticated user cannot update user details
    def test_update_user_unauthenticated(self):
        # Act: Make PUT request to edit user endpoint without authentication
        response = self.client.put(self.edit_user_url, self.update_data, format='json')

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    # test_update_user_non_admin_user(): Ensure that a non-admin user cannot update another user's details  
    def test_update_user_non_admin_user(self):
        # Arrange: Authenticate the staff user
        self.client.force_authenticate(user=self.regular_user)

        # Act: Make PUT request to edit user endpoint
        response = self.client.put(self.edit_user_url, self.update_data, format='json')

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'You do not have permission to perform this action.'})


class DeleteUserTests(APITestCase):
    def setUp(self):
        # Create a user who will perform the delete operations
        self.deleter_user = users.objects.create_user(
            username='deleteruser',
            email='deleteruser@example.com',
            password='deleterpassword',
            role='admin',
            date_of_hire='1980-08-08',
            first_name='Deleter',
            last_name='User',
            department='Deleting',
        )
        # Create a user who will be the target of delete operations
        self.target_user = users.objects.create_user(
            username='targetuser',
            email='targetuser@example.com',
            password='targetpassword',
            role='user',
            date_of_hire='1990-01-01',
            first_name='Target',
            last_name='User',
            department='Targeting',
        )
        # Create a regular user for testing
        self.regular_user = users.objects.create_user(
            username='staffuser',
            email='staffuser@example.com',
            password='staffpassword',
            role='user',
            date_of_hire='1990-01-01',
            first_name='Staff',
            last_name='User',
            department='Staffington',
        )

        self.client = APIClient()

        # Set up the URLs for deleting
        self.delete_user_url = reverse('delete_user', kwargs={'user_id': self.target_user.user_id})

    @patch('auth_app.models.users.objects.get')
    # test_delete_user_success(): Ensure that an authenticated user can delete another user
    def test_delete_user_success(self, mock_get):
        # Arrange: Mock user retrieval and authenticate the deleter user
        mock_get.return_value = self.target_user
        self.client.force_authenticate(user=self.deleter_user)

        # Act: Make DELETE request to delete user endpoint
        response = self.client.delete(self.delete_user_url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "User deleted successfully"})
    
    @patch('auth_app.models.users.objects.get')
    # test_delete_user_not_found(): Ensure that deleting a non-existent user returns a 404 error
    def test_delete_user_not_found(self, mock_get):
        # Arrange: Mock user retrieval to raise an exception, authenticate user, and set up URL
        mock_get.side_effect = users.DoesNotExist()
        self.client.force_authenticate(user=self.deleter_user)
        url = reverse('delete_user', kwargs={'user_id': 9999})
        
        # Act: Make DELETE request to delete user endpoint
        response = self.client.delete(url)

        # Arrange: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')

    @patch('auth_app.models.users.objects.get')
    # test_delete_user_server_error(): Ensure that an error during deletion returns a 500 error
    def test_delete_user_server_error(self, mock_get):
        # Arrange: Mock deletion to raise an exception and authenticate user
        mock_user = MagicMock()
        mock_get.return_value = mock_user
        mock_user.delete.side_effect = Exception("Database error")
        self.client.force_authenticate(user=self.deleter_user)

        # Act: Make DELETE request to delete user endpoint
        response = self.client.delete(self.delete_user_url)
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "An error occurred: Database error")

    # test_delete_user_unauthenticated(): Ensure that an unauthenticated user cannot delete a user
    def test_delete_user_unauthenticated(self):
        # Act: Make DELETE request to delete user endpoint without authentication
        response = self.client.delete(self.delete_user_url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    # test_delete_user_non_admin_user(): Ensure that a non-admin user cannot delete another user
    def test_delete_user_non_admin_user(self):
        # Arrange: Authenticate the staff user
        self.client.force_authenticate(self.regular_user)  

        # Act: Make DELETE request to delete user endpoint
        response = self.client.delete(self.delete_user_url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'You do not have permission to perform this action.'})