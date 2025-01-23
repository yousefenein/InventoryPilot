from rest_framework import serializers
from auth_app.models import users

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