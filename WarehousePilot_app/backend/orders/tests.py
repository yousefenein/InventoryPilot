"""

This file includes:
- Tests for generating manufacturing and inventory lists (`GenerateListsTests`).
- Tests for retrieving inventory picklist items (`InventoryPicklistItemsViewTest`).

"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Orders, OrderPart
from inventory.models import Inventory
from parts.models import Part


# Create your tests here.
class GenerateListsTests(APITestCase):
    def setUp(self):
        Orders.objects.create(order_id = 12345)
        
    def test_varied(self):
        print("___________ STARTING TEST test_varied _______________")
        order = Orders.objects.get(order_id = 12345)
        Part.objects.bulk_create(
            [
                Part(sku_color='equal to inventory'),
                Part(sku_color='more than inventory'),
                Part(sku_color='less than inventory'),
                Part(sku_color='not in inventory'),
            ]
        )
        parts = Part.objects.all()
        print("all created parts in test db:")
        for p in parts:
            print(p.sku_color)
        Inventory.objects.bulk_create(
            [
                Inventory(location = 'loc1Test', sku_color = parts[0], qty=10, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc2Test', sku_color = parts[1], qty=3, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc3Test', sku_color = parts[2], qty=8, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc4Test', sku_color = parts[2], qty=12, warehouse_number = 'TestHouse', amount_needed = 0),
            ]
        )
        OrderPart.objects.bulk_create(
            [
                OrderPart(order_id = order, sku_color = parts[0], qty = 10),
                OrderPart(order_id = order, sku_color=parts[1], qty = 10),
                OrderPart(order_id = order, sku_color=parts[2], qty = 10),
                OrderPart(order_id = order, sku_color=parts[3], qty = 10),
            ]
        )
        url = reverse('generateLists')
        response = self.client.post(url, {'orderID' : '12345'}, format='json')
        print('varied test case')
        print(response.data)
        pass
        
    def test_no_inventory_picklist(self):
        print("___________ STARTING TEST test_no_inventory_picklist _______________")
        order = Orders.objects.get(order_id = 12345)
        Part.objects.bulk_create(
            [
                Part(sku_color='not in inventory'),
            ]
        )
        parts = Part.objects.all()
        print("all created parts in test db:")
        for p in parts:
            print(p.sku_color)
        OrderPart.objects.bulk_create(
            [
                OrderPart(order_id = order, sku_color = parts[0], qty = 10),
            ]
        )
        url = reverse('generateLists')
        response = self.client.post(url, {'orderID' : '12345'}, format='json')
        print('no inventory picklist test case')
        print(response.data)
        pass
        
    def test_no_manuList(self):
        print("___________ STARTING TEST test_no_manuList _______________")
        order = Orders.objects.get(order_id = 12345)
        Part.objects.bulk_create(
            [
                Part(sku_color='only in inventory'),
            ]
        )
        parts = Part.objects.all()
        print("all created parts in test db:")
        for p in parts:
            print(p.sku_color)
        Inventory.objects.bulk_create(
            [
                Inventory(location = 'loc3Test', sku_color = parts[0], qty=8, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc4Test', sku_color = parts[0], qty=12, warehouse_number = 'TestHouse', amount_needed = 0),
            ]
        )
        OrderPart.objects.bulk_create(
            [
                OrderPart(order_id = order, sku_color = parts[0], qty = 5),
            ]
        )
        url = reverse('generateLists')
        response = self.client.post(url, {'orderID' : '12345'}, format='json')
        print('no manuList test case')
        print(response.data)
        pass   





from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from inventory.models import  InventoryPicklist, InventoryPicklistItem, users
from rest_framework_simplejwt.tokens import RefreshToken



class InventoryPicklistItemsViewTest(APITestCase):

    def setUp(self):
        # Create a mock user
        self.user = users.objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com",
            role="Employee",
            dob="1990-01-01",
            first_name="Test",
            last_name="User",
            department="Inventory"
        )

        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create a mock order
        self.order = Orders.objects.create(
            order_id=1,
            status="Pending",
            due_date="2025-01-30",
            estimated_duration=5
        )

        # Create a mock inventory picklist for the order
        self.picklist = InventoryPicklist.objects.create(
            order_id=self.order,
            assigned_employee_id=self.user,
            status=True
        )

        # Create a mock part
        self.part = Part.objects.create(
            sku_color="Blue",
            sku="ABC123",
            description="Test part",
            qty_per_box=10,
            weight=1.2
        )

        # Create a mock inventory location
        self.location = Inventory.objects.create(
            location="A1",
            sku_color=self.part,
            qty=100,
            warehouse_number="W1",
            amount_needed=5
        )

        # Create a mock inventory picklist item
        self.picklist_item = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist,
            location=self.location,
            sku_color=self.part,
            amount=5,
            status=False
        )

    def test_get_inventory_picklist_items_success(self):
        # Test successful retrieval of inventory picklist items
        url = reverse('inventory_picklist_items', kwargs={'order_id': self.order.order_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location'], "A1")
        self.assertEqual(response.data[0]['sku_color'], "Blue")
        self.assertEqual(response.data[0]['quantity'], 5)
        self.assertEqual(response.data[0]['status'], False)
        print("test_get_inventory_picklist_items_success passed.")

    def test_get_inventory_picklist_items_order_not_found(self):
        # Test when the order does not exist
        url = reverse('inventory_picklist_items', kwargs={'order_id': 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Order not found")
        print("test_get_inventory_picklist_items_order_not_found passed.")

    def test_get_inventory_picklist_items_no_picklist(self):
        # Test when no inventory picklist exists for the order
        order_without_picklist = Orders.objects.create(
            order_id=2,
            status="Pending",
            due_date="2025-02-01",
            estimated_duration=3
        )
        url = reverse('inventory_picklist_items', kwargs={'order_id': order_without_picklist.order_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "No picklist found for the given order")
        print("test_get_inventory_picklist_items_no_picklist passed.")