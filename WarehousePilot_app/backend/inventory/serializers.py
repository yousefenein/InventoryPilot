from rest_framework import serializers
from .models import InventoryPicklist
from auth_app.models import users

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ['id', 'first_name', 'last_name']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryPicklist
        fields = ['order_id', 'picklist_id', 'status', 'assigned_employee_id']