from rest_framework import serializers
from auth_app.models import users
from .models import AdminDashboardActivity, DashboardSettings

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ('user_id', 'username', 'email', 'role', 'dob', 'first_name', 'last_name', 'department', 'is_active', 'is_staff')
        read_only_fields = ('user_id', 'is_staff')  # Protect sensitive fields

    def validate_role(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_admin:
            raise serializers.ValidationError("Only admins can modify roles")
        return value

class AdminDashboardActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AdminDashboardActivity
        fields = ('id', 'user', 'user_name', 'action', 'timestamp', 'details')
        read_only_fields = ('timestamp',)

class DashboardSettingsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DashboardSettings
        fields = ('id', 'user', 'username', 'theme', 'notifications_enabled', 'last_modified')
        read_only_fields = ('last_modified',)

    def validate(self, data):
        # Ensure users can only modify their own settings unless they're admin
        request = self.context.get('request')
        if request and not request.user.is_admin:
            if data.get('user') and data['user'] != request.user:
                raise serializers.ValidationError("You can only modify your own settings")
        return data

class AdminDashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    admin_count = serializers.IntegerField()
    manager_count = serializers.IntegerField()
    recent_activities = AdminDashboardActivitySerializer(many=True)
