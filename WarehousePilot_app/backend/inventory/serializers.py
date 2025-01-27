from rest_framework import serializers
from .models import InventoryPicklist
from auth_app.models import users

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ['id', 'first_name', 'last_name']
        read_only_fields = ['role']  # Prevent role modification through this serializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryPicklist
        fields = ['order_id', 'picklist_id', 'status', 'assigned_employee_id']

    def validate(self, data):
        request = self.context.get('request')
        if request and not request.user.role in ['admin', 'manager']:
            # Regular users can only update status
            allowed_fields = {'status'}
            provided_fields = set(data.keys())
            if not provided_fields.issubset(allowed_fields):
                raise serializers.ValidationError("You can only update the status field")
        return data
