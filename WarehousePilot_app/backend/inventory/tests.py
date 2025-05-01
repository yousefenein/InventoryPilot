from django.test import TestCase, Client
from django.urls import reverse
from .models import Inventory
from parts.models import Part
import json
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import InventoryPicklist, InventoryPicklistItem
from orders.models import Orders
from django.utils import timezone
from rest_framework import status

User = get_user_model()

class InventoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.part = Part.objects.create(
            sku_color='ALOE 01',
            sku='ALOE',
            description='Aloe Part Description'
        )
        self.inventory_item = Inventory.objects.create(
            location="TEST",
            sku_color=self.part,
            qty=100,
            warehouse_number="499 B",
            amount_needed=50
        )

    def test_get_inventory(self):
        response = self.client.get(reverse('get_inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('inventory', response.json())
        inventory_data = response.json()['inventory']
        self.assertEqual(len(inventory_data), 1)
        self.assertEqual(inventory_data[0]['location'], self.inventory_item.location)
        self.assertEqual(inventory_data[0]['qty'], self.inventory_item.qty)
        self.assertEqual(inventory_data[0]['warehouse_number'], self.inventory_item.warehouse_number)
        self.assertEqual(inventory_data[0]['amount_needed'], self.inventory_item.amount_needed)

    def test_add_inventory_item(self):
        data = {
            "location": "Test ADD",
            "sku_color_id": self.part.sku_color,
            "qty": 200,
            "warehouse_number": "499 B",
            "amount_needed": 100
        }
        response = self.client.post(reverse('add_inventory_item'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['message'], "Item added successfully")
        
        new_item = Inventory.objects.get(location="Test ADD")
        self.assertEqual(new_item.qty, 200)
        self.assertEqual(new_item.warehouse_number, "499 B")
        self.assertEqual(new_item.amount_needed, 100)


    def test_delete_inventory_items(self):
        item_ids = [self.inventory_item.inventory_id]
        data = {"item_ids": item_ids}
        response = self.client.post(reverse('delete_inventory_items'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['message'], "Items deleted successfully")
        
        with self.assertRaises(Inventory.DoesNotExist):
            Inventory.objects.get(inventory_id=self.inventory_item.inventory_id)


class AssignedPicklistViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuseremail@test.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            role="staff",
            department="Test Department",
            date_of_hire=timezone.now(),
        )
        self.client = APIClient()
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create a test order
        self.order = Orders.objects.create(
            order_id="123",
            due_date=timezone.now() + timezone.timedelta(days=5),
            status="In Progress"
        )

        # Create a picklist assigned to the user
        self.picklist = InventoryPicklist.objects.create(
            order_id=self.order,
            assigned_employee_id=self.user,
            status=False,
        )
        #create part
        self.part = Part.objects.create(
            sku_color='ALOE 01',
            sku='ALOE',
            description='Aloe Part Description'
        )
        # Create picklist items
        self.picklist_item = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist,
            status=False,
            sku_color=self.part,
            amount=10,
        )
        self.url = reverse('assigned_inventory_picklist')
        
    def test_get_assigned_picklists_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["order_id"], int(self.order.order_id))
        self.assertEqual(response.data[0]["already_filled"], False)
        self.assertEqual(response.data[0]["assigned_to"], "Test User")

    def test_get_assigned_picklists_no_picklists(self):
        # Unassign the picklist from the user
        self.picklist.assigned_employee_id = None
        self.picklist.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([], response.data)

    def test_get_assigned_picklists_error(self):
        # Simulate an error by deleting the user
        self.user.delete()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_unathenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
