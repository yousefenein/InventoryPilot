from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from auth_app.models import users
from .serializers import StaffSerializer

User = get_user_model()

class ManageUsersViewTest(TestCase):
    def setUp(self):
        self.admin_user = users.objects.create_user(
            first_name='Test',
            last_name='Admin',
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            dob='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False
        )

        self.staff_user = users.objects.create_user(
            first_name='Test',
            last_name='Employee',
            username="employee",
            password="employeepassword",
            email="employee@example.com",
            dob='2025-12-29',
            department='Testing',
            role='user',
            is_staff=True
        )

        self.manage_users_url = reverse('manage_users')
        self.client = APIClient()

    def test_manage_users_authenticated_request(self):
        staff_data = users.objects.all()
        serializer = StaffSerializer(staff_data, many=True)
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        
        response = self.client.get(self.manage_users_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_manage_users_non_admin_user_request(self):
        refresh = RefreshToken.for_user(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        
        response = self.client.get(self.manage_users_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AddUserTests(APITestCase):
    def setUp(self):
        self.admin_user = users.objects.create_user(
            username='adminuser',
            email='adminuser@example.com',
            password='adminpassword',
            role='admin',
            dob='1980-08-08',
            first_name='Admin',
            last_name='User',
            department='Administration',
        )

        self.login_url = reverse('login')
        login_data = {
            'username': 'adminuser',
            'password': 'adminpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed in setUp.")
        self.access_token = response.data.get('access')
        self.add_user_url = reverse('add_user')

    def test_add_user_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        user_data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'newuser@example.com',
            'role': 'user',
            'first_name': 'New',
            'last_name': 'User',
            'department': 'Testing',
            'dob': '1995-05-15'
        }
        response = self.client.post(self.add_user_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User created successfully')

        user = users.objects.get(email='newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.role, 'user')

    def test_add_user_duplicate_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        user_data = {
            'username': 'anotheruser',
            'password': 'anotherpassword123',
            'email': 'adminuser@example.com',
            'role': 'user',
            'first_name': 'Another',
            'last_name': 'User',
            'department': 'Testing',
            'dob': '1990-05-15'
        }
        response = self.client.post(self.add_user_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User with this email already exists')

    def test_add_user_unauthenticated(self):
        user_data = {
            'username': 'unauthuser',
            'password': 'unauthpassword123',
            'email': 'unauthuser@example.com',
            'role': 'user',
            'first_name': 'Unauth',
            'last_name': 'User',
            'department': 'Testing',
            'dob': '2000-01-01'
        }
        response = self.client.post(self.add_user_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class EditUserTests(APITestCase):
    def setUp(self):
        self.editor_user = users.objects.create_user(
            username='editoruser',
            email='editoruser@example.com',
            password='editorpassword',
            role='admin',
            dob='1985-05-15',
            first_name='Editor',
            last_name='User',
            department='Editing',
        )

        self.target_user = users.objects.create_user(
            username='targetuser',
            email='targetuser@example.com',
            password='targetpassword',
            role='staff',
            dob='1990-01-01',
            first_name='Target',
            last_name='User',
            department='Targeting',
        )

        self.login_url = reverse('login')
        login_data = {
            'username': 'editoruser',
            'password': 'editorpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed in setUp.")
        self.access_token = response.data.get('access')
        self.edit_user_url = reverse('edit_user', kwargs={'user_id': self.target_user.user_id})

    def test_get_user_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.edit_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'targetuser')
        self.assertEqual(response.data['email'], 'targetuser@example.com')

    def test_update_user_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        update_data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'department': 'UpdatedDepartment',
        }
        response = self.client.put(self.edit_user_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully')

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.first_name, 'UpdatedFirstName')
        self.assertEqual(self.target_user.last_name, 'UpdatedLastName')
        self.assertEqual(self.target_user.department, 'UpdatedDepartment')

class DeleteUserTests(APITestCase):
    def setUp(self):
        self.deleter_user = users.objects.create_user(
            username='deleteruser',
            email='deleteruser@example.com',
            password='deleterpassword',
            role='admin',
            dob='1980-08-08',
            first_name='Deleter',
            last_name='User',
            department='Deleting',
        )

        self.target_user = users.objects.create_user(
            username='targetuser',
            email='targetuser@example.com',
            password='targetpassword',
            role='user',
            dob='1990-01-01',
            first_name='Target',
            last_name='User',
            department='Targeting',
        )

        self.login_url = reverse('login')
        login_data = {
            'username': 'deleteruser',
            'password': 'deleterpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed in setUp.")
        self.access_token = response.data.get('access')
        self.delete_user_url = reverse('delete_user', kwargs={'user_id': self.target_user.user_id})

    def test_delete_user_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(self.delete_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User deleted successfully')

        with self.assertRaises(users.DoesNotExist):
            users.objects.get(user_id=self.target_user.user_id)

    def test_delete_user_unauthenticated(self):
        response = self.client.delete(self.delete_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
