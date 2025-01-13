from django.urls import path
from .views import logs_from_frontend

urlpatterns = [
    path('log/', logs_from_frontend, name='log_from_frontend'),
]