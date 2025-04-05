"""
This file contains test cases for validating authentication
 It includes the following test classes:
1. `AuthTests`: Tests login functionality, including successful login and failure scenarios with invalid credentials.
2. `ChangePasswordTests`: Verifies the password change process, handling scenarios like correct, incorrect, or missing old passwords.
3. `ProfileViewTests`: Tests profile retrieval, including access for authenticated users, unauthenticated access, and handling invalid tokens.
4. `PasswordResetRequestTests`: Tests the password reset request process, including email validation and sending reset emails.
"""


from django.urls import reverse
from rest_framework import status, serializers
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import users
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from unittest.mock import patch
from .models import users
from .serializers import PasswordResetRequestSerializer, PasswordResetSerializer

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.user = users.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            role='user',
            date_of_hire='1990-01-01',
            first_name='Test',
            last_name='User',
            department='Testing',
            theme_preference='light'
        )   
        self.login_url = reverse('login')

    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS])

class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = users.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='oldpassword',
            role='user',
            date_of_hire='1990-01-01',
            first_name='Test',
            last_name='User',
            department='Testing',
        )   
        self.url = reverse('change_password')  
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        """
        Checks if the password is changed successfully and the user can login with the new password.
        """
        data = {
            'old_password': 'oldpassword',
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password changed successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_change_password_incorrect_old_password(self):
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Old password is incorrect')

    def test_change_password_missing_old_password(self):
        data = {
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ProfileViewTests(APITestCase):
    def setUp(self):
        self.user = users.objects.create_user(
            username='profileuser',
            email='profileuser@example.com',
            password='profilepass',
            role='user',
            date_of_hire='1990-01-01',
            first_name='Profile',
            last_name='Tester',
            department='QA',
        )
        # Login to get an access token
        self.login_url = reverse('login') 
        login_data = {
            'username': 'profileuser',
            'password': 'profilepass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed in setUp.")
        
        # Store tokens and set up the headers for authenticated requests
        self.access_token = response.data.get('access')
        self.profile_url = reverse('profile') # URL here 

    def test_profile_success(self):
        """
        Ensure that an authenticated user can retrieve their own profile data.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('role', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('department', response.data)
        
        self.assertEqual(response.data['username'], 'profileuser')
        self.assertEqual(response.data['email'], 'profileuser@example.com')
        self.assertEqual(response.data['role'], 'user')
        self.assertEqual(response.data['first_name'], 'Profile')
        self.assertEqual(response.data['last_name'], 'Tester')
        self.assertEqual(response.data['department'], 'QA')

    def test_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PasswordResetRequestTests(APITestCase):
    def setUp(self):
        # Create a test user with test values
        self.user = users.objects.create_user(
            first_name='Test',
            last_name='Tester',
            username="tester",
            password="testpassword",
            email="test@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False,
            theme_preference='light'
        )

        # Create an API client instance
        self.client = APIClient()

        # Test emails for valid and invalid cases
        self.valid_email = {'email': 'test@example.com'}
        self.invalid_email = {'email': 'nonexistent@example.com'}

        # backend URL for password reset request
        self.url = reverse('password_reset_request')  

    @patch('auth_app.serializers.users.objects.filter')
    # test_validate_email_exists(): Test validate_email() for existing email 
    def test_validate_email_exists(self, mock_filter):
        # Arrange: Mock the filter to return a user
        mock_filter.return_value.exists.return_value = True
        
        # Act: Call validate_email() with valid email
        serializer = PasswordResetRequestSerializer()
        result = serializer.validate_email('test@example.com')
        
        # Assert: Check if result = input email
        self.assertEqual(result, 'test@example.com')
        mock_filter.assert_called_once_with(email='test@example.com') 

    @patch('auth_app.serializers.users.objects.filter')
    # test_validate_email_not_exists(): Test validate_email() for nonexistent email
    def test_validate_email_not_exists(self, mock_filter):
        # Arrange: Mock the filter to return no user
        mock_filter.side_effect = serializers.ValidationError("User with this email does not exist.")
        

        # Act: Call validate_email() with a nonexistent email
        serializer = PasswordResetRequestSerializer()
        response = serializer.validate_email('nonexistent@example.com')

        # Assert: Check if exception is raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('auth_app.serializers.send_mail')
    @patch('auth_app.serializers.default_token_generator.make_token')
    @patch('auth_app.serializers.users.objects.get')
    # test_send_reset_email_success(): Test send_reset_email() for successful email sending
    def test_send_reset_email_success(self, mock_get, mock_make_token, mock_send_mail):
        # Arrange: Mock user retrieval and token generation
        mock_get.return_value = self.user
        mock_make_token.return_value = 'testtoken'
        
        # Act: Call send_reset_email() with valid email
        serializer = PasswordResetRequestSerializer()
        serializer.send_reset_email('test@example.com')
        
        # Assert: Check if email was sent and token was generated
        mock_get.assert_called_once_with(email='test@example.com')
        mock_make_token.assert_called_once_with(self.user)
        mock_send_mail.assert_called_once()

    @patch('auth_app.serializers.users.objects.get')
    # test_send_reset_email_user_not_found(): Test send_reset_email() for nonexistent user
    def test_send_reset_email_user_not_found(self, mock_get):
        # Arrange: Mock user retrieval to raise DoesNotExist exception
        mock_get.side_effect = users.DoesNotExist()
        
        # Act and Assert: Call send_reset_email() with nonexistent email and check for exception
        serializer = PasswordResetRequestSerializer()
        with self.assertRaises(users.DoesNotExist):
            serializer.send_reset_email('nonexistent@example.com')
        mock_get.assert_called_once()
        

    @patch('auth_app.serializers.PasswordResetRequestSerializer')
    # test_password_reset_request_view_success(): Test PasswordResetRequestView for processing a successful request
    def test_password_reset_request_view_success(self, mock_serializer):
        # Arrange: Mock the serializer
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.validate_email.return_value = 'test@example.com'
        mock_serializer_instance.send_reset_email.return_value = None
        
        # Act: Call PasswordResetRequestView with valid email
        response = self.client.post(self.url, self.valid_email)
        
        # Assert: Check if the response is as expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Password reset email sent."})

