from rest_framework import serializers
from auth_app.models import users

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ('user_id','role','first_name', 'last_name', 'department')
    
    def validate_role(self, value):
        """
        Validate that the role is one of the predefined choices
        """
        if value not in dict(users.Roles.choices):
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(dict(users.Roles.choices).keys())}"
            )
        return value

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = users
        fields = ('username', 'email', 'password', 'role', 'first_name', 
                 'last_name', 'department', 'dob', 'user_id')
        read_only_fields = ('user_id',)

    def validate_role(self, value):
        if value not in dict(users.Roles.choices):
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(dict(users.Roles.choices).keys())}"
            )
        return value

    def create(self, validated_data):
        user = users.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ('role', 'first_name', 'last_name', 'department', 'email')
        
    def validate_role(self, value):
        if value not in dict(users.Roles.choices):
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(dict(users.Roles.choices).keys())}"
            )
        return value