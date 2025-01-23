from django.urls import path
from .views import (
    LoginView, 
    ChangePasswordView, 
    ProfileView, 
    RetrieveUsers,
    AdminOnlyView,
    ManagerOnlyView,
    UserRoleUpdateView,
    UserCreateView,
    UserDeleteView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('retrieve_users/', RetrieveUsers.as_view(), name='retrieve_users'),
 
     # New role-based routes
    path('admin/dashboard/', AdminOnlyView.as_view(), name='admin_dashboard'),
    path('manager/dashboard/', ManagerOnlyView.as_view(), name='manager_dashboard'),
    
    # User management routes
    path('users/', UserManagementView.as_view(), name='user_list_create'),
    path('users/<int:user_id>/', UserManagementView.as_view(), name='user_detail'),
]