from django.urls import path
from .views import ManagerDashboardView

urlpatterns = [
    path('', ManagerDashboardView.as_view(), name='manager_dashboard'),
]