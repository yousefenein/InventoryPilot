from django.urls import path

from . import views
from .views import InventoryView
from auth_app.views import ProfileView
from inventory.views import AssignOrderView, AssignedPicklistView, PickPicklistItemView

urlpatterns = [
    path("", views.get_inventory, name="get_inventory"),
    path("delete", views.delete_inventory_items, name="delete_inventory_items"),
    path("csrf-token", views.get_csrf_token, name="get_csrf_token"),
    path("add", views.add_inventory_item, name="add_inventory_item"),
    path("inventorypreview/", InventoryView.as_view(), name="inventorypreview"),
    path('auth/staff', ProfileView.as_view(), name='staff_list'),
    path('assign_order/<int:order_id>', AssignOrderView.as_view(), name='assign_order'),
    path('assigned_inventory_picklist/', AssignedPicklistView.as_view(), name='assigned_inventory_picklist'),
    path('inventory_picklist_items/<int:picklist_item_id>/pick/', PickPicklistItemView.as_view(), name='pick_picklist_item'),
]