from django.urls import path
from .views import LoginView, ChangePasswordView, PasswordResetView, ProfileView, RetrieveUsers, ThemePreferenceView, PasswordResetRequestView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('retrieve_users/', RetrieveUsers.as_view(), name='retrieve_users'),
    path('theme/', ThemePreferenceView.as_view(), name='theme_preference'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset')
]
