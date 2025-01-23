from django.urls import path
from .views import (
    ManageUsersView, 
    AddUserView, 
    EditUserView, 
    DeleteUserView,
    AdminDashboardActivityView,
    DashboardSettingsView
)

urlpatterns = [
    # User management URLs
    path('manage_users/', ManageUsersView.as_view(), name='manage_users'),
    path('add_user/', AddUserView.as_view(), name='add_user'),
    path('edit_user/<int:user_id>/', EditUserView.as_view(), name='edit_user'),
    path('delete_user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
    
    # Dashboard activity and settings
    path('activity/', AdminDashboardActivityView.as_view(), name='dashboard_activity'),
    path('settings/', DashboardSettingsView.as_view(), name='dashboard_settings'),
    path('settings/<int:user_id>/', DashboardSettingsView.as_view(), name='user_dashboard_settings'),
]
