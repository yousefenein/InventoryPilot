"""

This file includes:
- Tests for generating manufacturing and inventory lists (`GenerateListsTests`).
- Tests for retrieving inventory picklist items (`InventoryPicklistItemsViewTest`).
- Tests for retrieving inventory picklist ( A.K.A orders that have been started )
- Tests for cycle time per order (`CycleTimePerOrderViewTests`).
"""

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from datetime import date  
from auth_app.models import users
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.db.models.query import QuerySet
from django.test import TestCase, override_settings
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from django.db import connection
from unittest.mock import patch, MagicMock
from .models import (
    Orders,
    OrderPart,
    Part
)
from inventory.models import (
    Inventory,
    InventoryPicklist,
    InventoryPicklistItem,
)
from manufacturingLists.models import (
    ManufacturingLists,
    ManufacturingListItem
)

class GenerateInventoryAndManufacturingListsViewTests(TestCase):
    def setUp(self):
        # Set up the test client and URL for the view
        self.client = APIClient()
        self.url = reverse('generateLists')
        self.order_id = 123

        # Create a test admin user
        self.admin_user = users.objects.create_user(
            first_name='Test',
            last_name='Admin',
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False
        )
        
        # Create a real order instance for testing
        self.mock_order = Orders.objects.create(order_id=self.order_id, status="Pending")
        
        # Mock order parts
        self.mock_order_part1 = MagicMock(spec=OrderPart)
        self.mock_order_part1.sku_color = "SKU001-RED"
        self.mock_order_part1.qty = 10
        self.mock_order_part1.location = "Location1"
        self.mock_order_part1.area = "Area1"
        self.mock_order_part1.lineup_nb = "Lineup1"
        self.mock_order_part1.final_model = "Model1"
        self.mock_order_part1.material_type = "Material1"
        self.mock_order_part1.order_id = self.mock_order
        
        self.mock_order_part2 = MagicMock(spec=OrderPart)
        self.mock_order_part2.sku_color = "SKU002-BLUE"
        self.mock_order_part2.qty = 5
        self.mock_order_part2.location = "Location2"
        self.mock_order_part2.area = "Area2"
        self.mock_order_part2.lineup_nb = "Lineup2"
        self.mock_order_part2.final_model = "Model2"
        self.mock_order_part2.material_type = "Material2"
        self.mock_order_part2.order_id = self.mock_order

        # Create real part instances for testing
        self.part1 = Part.objects.create(sku_color="SKU001-RED", sku="SKU001", description="Test Part 1", qty_per_box=10, weight=1.2)
        self.part2 = Part.objects.create(sku_color="SKU002-BLUE", sku="SKU002", description="Test Part 2", qty_per_box=5, weight=0.8)
        
        # Mock inventory items
        self.mock_inventory1 = MagicMock(spec=Inventory)
        self.mock_inventory1.sku_color = "SKU001-RED"
        self.mock_inventory1.qty = 8
        self.mock_inventory1.amount_needed = 0
        self.mock_inventory1.location = "Location1"
        
        self.mock_inventory2 = MagicMock(spec=Inventory)
        self.mock_inventory2.sku_color = "SKU001-RED"
        self.mock_inventory2.qty = 4
        self.mock_inventory2.amount_needed = 0
        self.mock_inventory2.location = "Location1A"
        
        # Mock picklist and manufacturing list
        self.mock_picklist = MagicMock(spec=InventoryPicklist, order_id=self.mock_order, status=False)
        self.mock_manu_list = ManufacturingLists(order_id=self.mock_order, status='Pending')
        
        # Mock picklist items and manufacturing list items
        self.mock_picklist_item = MagicMock(spec=InventoryPicklistItem)
        self.mock_manu_list_item = MagicMock(spec=ManufacturingListItem)
    
    @patch('orders.models.Orders.objects.get')
    @patch('orders.models.OrderPart.objects.filter')
    @patch('inventory.models.Inventory.objects.filter')
    @patch('inventory.models.InventoryPicklist.objects.create')
    @patch('manufacturingLists.models.ManufacturingLists.objects.create')
    @patch('inventory.models.InventoryPicklistItem.objects.bulk_create')
    @patch('manufacturingLists.models.ManufacturingListItem.objects.bulk_create')
    # test_generate_lists_with_inventory_match(): Test the case when the order parts match the inventory items
    def test_generate_lists_with_inventory_match(
        self, mock_manu_bulk_create, mock_inv_bulk_create, 
        mock_manu_create, mock_picklist_create, mock_inv_filter, 
        mock_order_part_filter, mock_order_get
    ):
        # Arrange: Mocking the order, order parts, inventory, picklist, and manufacturing list; and authenticating user
        mock_order_get.return_value = self.mock_order

        mock_order_part_filter.return_value = MagicMock(
            spec=QuerySet,
            values_list=MagicMock(return_value=["SKU001-RED", "SKU002-BLUE"]),
            __iter__=MagicMock(return_value=iter([
                OrderPart(order_id=self.mock_order, sku_color=self.part1, qty=10),
                OrderPart(order_id=self.mock_order, sku_color=self.part2, qty=5)
            ]))
        )

        mock_inv_filter.return_value = MagicMock(
            spec=QuerySet,
            aggregate=MagicMock(return_value={'total': 12}),  
            values_list=MagicMock(return_value=["SKU001-RED"]),
            order_by=MagicMock(return_value=[self.mock_inventory1, self.mock_inventory2]),
            count=MagicMock(return_value=2)
        )

        mock_picklist_create.return_value = self.mock_picklist
        mock_manu_create.return_value = self.mock_manu_list

        self.client.force_authenticate(user=self.admin_user)

        # Act: Make POST request to generate lists
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "inventory picklist and manufacturing list generation successful")

    @patch('orders.models.Orders.objects.get')
    @patch('orders.models.OrderPart.objects.filter')
    @patch('inventory.models.Inventory.objects.filter')
    @patch('manufacturingLists.models.ManufacturingLists.objects.create')
    @patch('manufacturingLists.models.ManufacturingListItem.objects.bulk_create')
    @patch('inventory.models.InventoryPicklist.objects.get_or_create')
    # test_generate_lists_no_inventory_match(): Test the case when no order parts match inventory items
    def test_generate_lists_no_inventory_match(
        self, mock_picklist_get_or_create, mock_manu_bulk_create,
        mock_manu_create, mock_inv_filter, mock_order_part_filter, 
        mock_order_get
    ):
        # Arrange: Mocking instances of models and authenticate user
        mock_order_get.return_value = self.mock_order

        mock_order_part_filter.return_value = MagicMock(
            spec=QuerySet,
            values_list=MagicMock(return_value=["SKU001-RED", "SKU002-BLUE"]),
            __iter__=MagicMock(return_value=iter([
                OrderPart(order_id=self.mock_order, sku_color=self.part1, qty=10),
                OrderPart(order_id=self.mock_order, sku_color=self.part2, qty=5)
            ]))
        )

        mock_inv_filter.return_value = MagicMock(
            spec=QuerySet,
            exists=MagicMock(return_value=False),
            values_list=MagicMock(return_value=[])
        )

        mock_manu_create.return_value = self.mock_manu_list
        mock_picklist_get_or_create.return_value = (self.mock_picklist, True)

        InventoryPicklist.objects.create(order_id=self.mock_order, status=False)

        self.client.force_authenticate(user=self.admin_user)

        # Act: Make POST request to generate lists
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_manu_create.assert_called_once_with(status='Pending', order_id=self.mock_order)
        self.assertTrue(mock_manu_bulk_create.called)

    @patch('orders.models.Orders.objects.get')
    @patch('orders.models.OrderPart.objects.filter')
    @patch('inventory.models.Inventory.objects.filter')
    @patch('manufacturingLists.models.ManufacturingLists.objects.create')
    @patch('manufacturingLists.models.ManufacturingListItem.objects.bulk_create')
    @patch('inventory.models.InventoryPicklist.objects.get_or_create')
    @patch('parts.models.Part.objects.get')
    # test_generate_lists_partial_inventory_match(): Test the case when some order parts match inventory items
    def test_generate_lists_partial_inventory_match(
        self, mock_part_get, mock_picklist_get_or_create, mock_manu_bulk_create,
        mock_manu_create, mock_inv_filter, mock_order_part_filter, 
        mock_order_get
    ):
        # Arrange: Mocking instances of models and authenticating user
        mock_order_get.return_value = self.mock_order

        mock_part_get.side_effect = lambda sku_color: self.part1 if sku_color == "SKU001-RED" else self.part2

        mock_order_parts = MagicMock(spec=QuerySet)
        mock_order_parts.values_list.return_value = ["SKU001-RED", "SKU002-BLUE"]
        mock_order_part_filter.return_value = mock_order_parts

        mock_inventory_qs = MagicMock(spec=QuerySet)
        mock_inventory_qs.count.return_value = 2 
        mock_inventory_qs.__iter__.return_value = iter([
            self.mock_inventory1,
            self.mock_inventory2
        ])
        mock_inv_filter.return_value = mock_inventory_qs

        InventoryPicklist.objects.create(order_id=self.mock_order, status=False)

        mock_manu_create.return_value = self.mock_manu_list
        mock_picklist_get_or_create.return_value = (self.mock_picklist, True)

        self.client.force_authenticate(user=self.admin_user)

        # Act: Make POST request to generate lists
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "inventory picklist and manufacturing list generation successful")
        self.assertTrue(mock_manu_bulk_create.called)

    @patch('orders.models.Orders.objects.get')
    # test_generate_lists_order_not_found(): Test the case when order doesn't exist
    def test_generate_lists_order_not_found(self, mock_order_get):
        # Arrange: Mocking order not found and authenticating user
        mock_order_get.side_effect = Orders.DoesNotExist
        self.client.force_authenticate(user=self.admin_user)

        # Act: Make POST request to generate lists with non-existing order ID
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')

        # Assert: Check if exception was raised and response status code is 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Order not found")

    @patch('orders.models.Orders.objects.get')
    @patch('orders.models.OrderPart.objects.filter')
    @patch('inventory.models.Inventory.objects.filter')
    @patch('manufacturingLists.models.ManufacturingLists.objects.create')
    @patch('manufacturingLists.models.ManufacturingListItem.objects.bulk_create')
    @patch('inventory.models.InventoryPicklist.objects.filter')
    # test_generate_lists_no_picklist(): Test the case when picklist doesn't exist
    def test_generate_lists_no_picklist(
        self, mock_picklist_filter, mock_manu_bulk_create,
        mock_manu_create, mock_inv_filter, mock_order_part_filter, 
        mock_order_get
    ):
        # Arrange: Mocking instances of models and authenticating user
        mock_order_get.return_value = self.mock_order

        mock_picklist_filter.return_value = MagicMock(
            exists=MagicMock(return_value=False)
        )

        mock_order_part_filter.return_value = MagicMock(
            spec=QuerySet,
            values_list=MagicMock(return_value=["SKU001-RED", "SKU002-BLUE"]),
            __iter__=MagicMock(return_value=iter([
                OrderPart(order_id=self.mock_order, sku_color=self.part1, qty=10),
                OrderPart(order_id=self.mock_order, sku_color=self.part2, qty=5)
            ]))
        )

        mock_inv_filter.return_value = MagicMock(
            spec=QuerySet,
            exists=MagicMock(return_value=False),
            values_list=MagicMock(return_value=[])
        )

        mock_manu_create.return_value = self.mock_manu_list

        self.client.force_authenticate(user=self.admin_user)

        # Act: Make POST request to generate lists
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "inventory picklist and manufacturing list generation successful")

    # test_generate_lists_unauthenticated(): Test the case when user is not authenticated
    def test_generate_lists_unauthenticated(self):        
        # Act: Make POST request to generate lists without authentication
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    # test_generate_lists_unauthorized(): Test the case when user is authenticated but not authorized (not admin or manager)
    def test_generate_lists_unauthorized(self):
        # Arrange: Change user role to 'user' and authenticate
        self.admin_user.role = 'user'  # Change role to non-admin
        self.admin_user.save()

        self.client.force_authenticate(user=self.admin_user)

        # Act: Make POST request to generate lists
        response = self.client.post(self.url, {'orderID': self.order_id}, format='json')

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")


class InventoryPicklistItemsViewTest(APITestCase):

    def setUp(self):
        #  a mock user
        self.user = users.objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com",
            role="Employee",
            date_of_hire="1990-01-01",
            first_name="Test",
            last_name="User",
            department="Inventory"
        )

        # JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        #  a mock order
        self.order = Orders.objects.create(
            order_id=1,
            status="Pending",
            due_date="2025-01-30",
            estimated_duration=5
        )

        #  a mock inventory picklist for the order
        self.picklist = InventoryPicklist.objects.create(
            order_id=self.order,
            assigned_employee_id=self.user,
            status=True
        )

        # a mock part
        self.part = Part.objects.create(
            sku_color="Blue",
            sku="ABC123",
            description="Test part",
            qty_per_box=10,
            weight=1.2
        )

        #  a mock inventory location
        self.location = Inventory.objects.create(
            location="A1",
            sku_color=self.part,
            qty=100,
            warehouse_number="W1",
            amount_needed=5
        )

        #  a mock inventory picklist item
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


class InventoryPicklistViewTest(APITestCase):
    def setUp(self):
        #  a mock user
        self.user = users.objects.create_user(
            username="testuser",
            password="password",
            email="testuser@example.com",
            role="Employee",
            date_of_hire="1990-01-01",
            first_name="Test",
            last_name="User",
            department="Inventory"
        )

        #  mock orders
        self.order1 = Orders.objects.create(order_id=1, status="In Progress", due_date=date(2025, 2, 15))
        self.order2 = Orders.objects.create(order_id=2, status="In Progress", due_date=date(2025, 2, 20))
        self.order3 = Orders.objects.create(order_id=3, status="Pending", due_date=date(2025, 3, 1))  # Not started

        #  a mock inventory picklist for order1 (partially filled)
        self.picklist1 = InventoryPicklist.objects.create(order_id=self.order1, assigned_employee_id=self.user, status=True)
        self.part1 = Part.objects.create(sku_color="Blue")
        self.item1 = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist1,
            location=None,
            sku_color=self.part1,
            amount=10,
            status=False
        )

        # a mock inventory picklist for order2 (completely filled)
        self.picklist2 = InventoryPicklist.objects.create(order_id=self.order2, assigned_employee_id=self.user, status=True)
        self.part2 = Part.objects.create(sku_color="Red")
        self.item2 = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist2,
            location=None,
            sku_color=self.part2,
            amount=5,
            status=True
        )

    def test_get_inventory_picklist_success(self):
        print("Running: test_get_inventory_picklist_success")
        # Authenticate as the user
        self.client.force_authenticate(user=self.user)

        url = reverse('inventory_picklist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only `In Progress` orders should be included

        # Verify order1 details
        order1 = response.data[0]
        self.assertEqual(order1["order_id"], 1)
        self.assertFalse(order1["already_filled"])  # Partially filled
        self.assertEqual(order1["assigned_to"], "testuser")

        # Verify order2 details 
        order2 = response.data[1]
        self.assertEqual(order2["order_id"], 2)
        self.assertTrue(order2["already_filled"])  # Completely filled
        self.assertEqual(order2["assigned_to"], "testuser")

        print("Passed: test_get_inventory_picklist_success")

    def test_get_inventory_picklist_no_in_progress_orders(self):
        print("Running: test_get_inventory_picklist_no_in_progress_orders")
        # Update orders to have no "In Progress" status
        self.order1.status = "Completed"
        self.order1.save()
        self.order2.status = "Completed"
        self.order2.save()

        # Authenticate as the user
        self.client.force_authenticate(user=self.user)

        url = reverse('inventory_picklist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No "In Progress" orders

        print("Passed: test_get_inventory_picklist_no_in_progress_orders")

    def test_unauthenticated_access(self):
        print("Running: test_unauthenticated_access")
        # Test without authentication
        url = reverse('inventory_picklist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print("Passed: test_unauthenticated_access")

class CycleTimePerOrderViewTests(APITestCase):
    # setUp(): used to set up values shared between tests.
    def setUp(self):
        # Create a test user with test values
        self.user = users.objects.create_user(
            first_name='Test',
            last_name='Admin',
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False,
            theme_preference='light'
        )

        # Create an API client instance
        self.client = APIClient()

        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Backend URL for the InventoryPickingLogging endpoint
        self.url = reverse('cycle_time_per_order') 

    @patch('orders.models.Orders.objects.all')
    @patch('inventory.models.InventoryPicklist.objects.all')
    @patch('inventory.models.InventoryPicklistItem.objects.all')
    # test_get_fully_completed_order(): Test the successful retrieval of cycle time data for a fully completed order
    def test_get_fully_completed_order(self, mock_picklist_item, mock_picklist, mock_orders):
        # Arrange: Mocking Orders, InventoryPicklist, and InventoryPicklistItem models
        mock_orders.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=5),
                'end_timestamp': timezone.now() - timedelta(days=3),
                'ship_date': (timezone.now() - timedelta(days=1)).date()
            }
        ]
        mock_picklist.return_value.values.return_value.filter.return_value.first.return_value = {
            'picklist_complete_timestamp': timezone.now() - timedelta(days=4),
            'picklist_id': 1,
            'order_id': 1
        }
        mock_picklist_item.return_value.values.return_value.filter.return_value.order_by.return_value = [
            {
                'picked_at': timezone.now() - timedelta(days=4, hours=2), 
                'picklist_id': 1
            },
            {
                'picked_at': timezone.now() - timedelta(days=6, hours=2), 
                'picklist_id': 1
            }
        ]

        # Act: Make a GET request to CycleTimePerOrderView        
        response = self.client.get(self.url)

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_id'], 1)
        self.assertEqual(response.data[0]['pick_time'], 1)  
        self.assertEqual(response.data[0]['pack_time'], 1)  
        self.assertEqual(response.data[0]['ship_time'], 2)  
        self.assertEqual(response.data[0]['cycle_time'], 4)  
        self.assertEqual(response.data[0]['status'], 'Shipped')

    @patch('orders.models.Orders.objects.all')
    @patch('inventory.models.InventoryPicklist.objects')
    # test_get_order_with_no_picklist(): Test the case when there are no picklists available for an order
    def test_get_order_with_no_picklist(self, mock_picklist, mock_orders):        
        # Arrange: Mocking Orders and InventoryPicklist models to simulate no picklist
        mock_orders.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=5),
                'end_timestamp': timezone.now() - timedelta(days=3),
                'ship_date': (timezone.now() - timedelta(days=1)).date()
            }
        ]
        mock_picklist.all.return_value.values.return_value.filter.return_value.first.side_effect = InventoryPicklist.DoesNotExist
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch('orders.models.Orders.objects')
    @patch('inventory.models.InventoryPicklist.objects')
    @patch('inventory.models.InventoryPicklistItem.objects')
    # test_get_order_not_fully_picked(): Test the case when an order is not fully picked
    def test_get_order_not_fully_picked(self, mock_picklist_item, mock_picklist, mock_orders):
        # Arrange: Mocking Orders, InventoryPicklist, and InventoryPicklistItem models where not all items are picked
        mock_orders.all.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=5)
            }
        ]
        mock_picklist.all.return_value.values.return_value.filter.return_value.first.return_value = {
            'picklist_complete_timestamp': None,
            'picklist_id': 1,
            'order_id': 1
        }
        mock_picklist_item.all.return_value.values.return_value.filter.return_value.order_by.return_value = [
            {
                'picked_at': timezone.now() - timedelta(days=4), 
                'picklist_id': 1
            },
            {
                'picked_at': None, 
                'picklist_id': 1
            }
        ]
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch('orders.models.Orders.objects')
    @patch('inventory.models.InventoryPicklist.objects')
    @patch('inventory.models.InventoryPicklistItem.objects')
    # test_get_order_picked_but_not_packed(): Test the case when an order is picked but not packed
    def test_get_order_picked_but_not_packed(self, mock_picklist_item, mock_picklist, mock_orders):        
        # Arrange: Mocking Orders, InventoryPicklist, and InventoryPicklistItem models where order is picked but not packed
        mock_orders.all.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=5),
                'end_timestamp': None,
                'ship_date': None
            }
        ]
        mock_picklist.all.return_value.values.return_value.filter.return_value.first.return_value = {
            'picklist_complete_timestamp': timezone.now() - timedelta(days=4),
            'picklist_id': 1,
            'order_id': 1,
        }
        mock_picklist_item.all.return_value.values.return_value.filter.return_value.order_by.return_value = [
            {
                'picked_at': timezone.now() - timedelta(days=4), 
                'picklist_id': 1
            },
        ]
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_id'], 1)
        self.assertEqual(response.data[0]['pick_time'], 1)
        self.assertEqual(response.data[0]['pack_time'], 0)
        self.assertEqual(response.data[0]['ship_time'], 0)
        self.assertEqual(response.data[0]['cycle_time'], 1)
        self.assertEqual(response.data[0]['status'], 'Picked')

    @patch('orders.models.Orders.objects')
    @patch('inventory.models.InventoryPicklist.objects')
    @patch('inventory.models.InventoryPicklistItem.objects')
    # test_get_order_packed_but_not_shipped(): Test the case when an order is picked and packed but not shipped
    def test_get_order_packed_but_not_shipped(self, mock_picklist_item, mock_picklist, mock_orders):
        # Arrange: Mocking Orders, InventoryPicklist, and InventoryPicklistItem models where order is not shipped
        mock_orders.all.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=5),
                'end_timestamp': timezone.now() - timedelta(days=3),
                'ship_date': None
            }
        ]
        mock_picklist.all.return_value.values.return_value.filter.return_value.first.return_value = {
            'picklist_complete_timestamp': timezone.now() - timedelta(days=4),
            'picklist_id': 1,
            'order_id': 1
        }
        mock_picklist_item.all.return_value.values.return_value.filter.return_value.order_by.return_value = [
            {
                'picked_at': timezone.now() - timedelta(days=4), 
                'picklist_id': 1
            }
        ]
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_id'], 1)
        self.assertEqual(response.data[0]['pick_time'], 1)
        self.assertEqual(response.data[0]['pack_time'], 1)
        self.assertEqual(response.data[0]['ship_time'], 0)
        self.assertEqual(response.data[0]['cycle_time'], 2)
        self.assertEqual(response.data[0]['status'], 'Packed')

    @patch('orders.models.Orders.objects')
    @patch('inventory.models.InventoryPicklist.objects')
    @patch('inventory.models.InventoryPicklistItem.objects')
    # test_get_order_with_no_picklist_timestamp__fully_picked(): Test the case when an order's picklist completion timestamp not set but all items are picked
    def test_get_order_with_no_picklist_timestamp__fully_picked(self, mock_picklist_item, mock_picklist, mock_orders):   
        # Arrange: Mocking Orders, InventoryPicklist, and InventoryPicklistItem models where picklist timestamp is None but all items are picked
        mock_orders.all.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=5),
                'end_timestamp': timezone.now() - timedelta(days=3),
                'ship_date': (timezone.now() - timedelta(days=1)).date()
            }
        ]
        mock_picklist.all.return_value.values.return_value.filter.return_value.first.return_value = {
            'picklist_complete_timestamp': None,
            'picklist_id': 1,
            'order_id': 1

        }
        mock_picklist_item.all.return_value.values.return_value.filter.return_value.order_by.return_value = [
            {
                'picked_at': timezone.now() - timedelta(days=4, hours=2)
            },
            {
                'picked_at': timezone.now() - timedelta(days=4, hours=1)
            }
        ]
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_id'], 1)
        self.assertEqual(response.data[0]['status'], 'Shipped')

    @patch('orders.models.Orders.objects')
    @patch('inventory.models.InventoryPicklist.objects')
    # test_get_order_past_month(): Test the case when an order is older than the past month
    def test_get_order_past_month(self, mock_picklist, mock_orders):
        # Arrange: Mocking Orders, InventoryPicklist, and InventoryPicklistItem models where order is older the past month       
        mock_orders.all.return_value.values.return_value.filter.return_value = [
            {
                'order_id': 1,
                'start_timestamp': timezone.now() - timedelta(days=35)
            }
        ]
        mock_picklist.all.return_value.values.return_value.filter.return_value.first.return_value = {
            'picklist_complete_timestamp': timezone.now() - timedelta(days=32),
            'picklist_id': 1,
            'order_id': 1
        }
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch('orders.models.Orders.objects')
    # test_no_orders_found(): Test the case when no orders are found
    def test_no_orders_found(self, mock_orders):
        # Arrange: Mocking Orders to return an empty list
        mock_orders.all.return_value.values.return_value.filter.return_value = []
        
        # Act: Make a GET request to CycleTimePerOrderView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class OrdersViewTests(TestCase):
    def setUp(self):
        # Create a client instance and setup url
        self.client = APIClient()
        self.url = reverse('ordersview')

        # Create a test user with test values
        self.user = users.objects.create_user(
            first_name='Test',
            last_name='Admin',
            username="admin",
            password="adminpassword",
            email="admin@example.com",
            date_of_hire='1990-01-01',
            department='Testing',
            role='admin',
            is_staff=False,
            theme_preference='light'
        )
        
        # Sample test data
        self.test_data = [
            (1, 120, 'Pending', '2023-12-31', None),
            (2, 60, 'In Progress', '2023-12-15', '2023-12-01 10:00:00')
        ]
        
    @patch('django.db.connection.cursor')
    # test_get_orders_success(): Test the successful retrieval of orders
    def test_get_orders_success(self, mock_cursor_func):
        # Arrange: Mocking the database cursor and connection, and authenticate user
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = self.test_data
        
        mock_cursor_func.return_value.__enter__.return_value = mock_cursor
        
        self.client.force_authenticate(user=self.user)
        
        # Act: Make a GET request to OrdersView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['order_id'], 1)
        self.assertEqual(response.data[1]['status'], 'In Progress')
        mock_cursor.execute.assert_called_once()
    
    # test_get_orders_unauthenticated(): Test the case when user is not authenticated
    def test_get_orders_unauthenticated(self):
        # Act: Make a GET request to OrdersView without authentication
        response = self.client.get(self.url)
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    # test_get_orders_unauthorized(): Test the case when user is authenticated but not authorized (not admin or manager)
    def test_get_orders_unauthorized(self):
        # Arrange: Change user role to 'user' and authenticate
        self.user.role = 'user'  # Change role to non-admin
        self.user.save()

        self.client.force_authenticate(user=self.user)

        # Act: Make a GET request to OrdersView
        response = self.client.get(self.url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")
    
    @patch('django.db.connection.cursor')
    # test_get_orders_database_error(): Test the case when there is a database error
    def test_get_orders_database_error(self, mock_cursor_func):
        # Arrange: Mock database to raise an exception and authenticate user
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_cursor_func.return_value.__enter__.return_value = mock_cursor
        
        self.client.force_authenticate(user=self.user)

        # Act: Make a GET request to OrdersView
        response = self.client.get(self.url)
        
        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], "Database error")
    
    @patch('django.db.connection.cursor')
    # test_empty_result_set(): Test handling of empty result set from database
    def test_empty_result_set(self, mock_cursor_func):
        # Arrange: Mock empty database result and authenticate user
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []
        
        mock_cursor_func.return_value.__enter__.return_value = mock_cursor
        
        self.client.force_authenticate(user=self.user)
        
        # Act: Make a GET request to OrdersView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch('django.db.connection.cursor')
    # test_null_start_timestamp_handling(): Test proper handling of NULL start_timestamp values
    def test_null_start_timestamp_handling(self, mock_cursor_func):
        # Arrange: Mock database to return NULL start_timestamp and authenticate user
        test_data = [(3, 90, 'Pending', '2023-12-20', None)]
        
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = test_data
        
        mock_cursor_func.return_value.__enter__.return_value = mock_cursor
        
        self.client.force_authenticate(user=self.user)

        # Act: Make a GET request to OrdersView
        response = self.client.get(self.url)
        
        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data[0]['start_timestamp'])