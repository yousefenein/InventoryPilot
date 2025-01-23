from django.db import models
from auth_app.models import users

#Tracks admin activities and actions in the dashboard
class AdminDashboardActivity(models.Model):
    user = models.ForeignKey(users, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Admin Activity'
        verbose_name_plural = 'Admin Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

# Stores admin dashboard configuration and preferences
class DashboardSettings(models.Model):
    user = models.OneToOneField(users, on_delete=models.CASCADE)
    theme = models.CharField(max_length=50, default='light')
    notifications_enabled = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dashboard Setting'
        verbose_name_plural = 'Dashboard Settings'

    def __str__(self):
        return f"Settings for {self.user.username}"
