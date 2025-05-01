"""

This file includes:
- Tests for generating manufacturing and inventory lists (`GenerateInventoryAndManufacturingListsViewTests`).
- Tests for retrieving inventory picklist items (`InventoryPicklistItemsViewTest`).
- Tests for retrieving inventory picklist ( A.K.A orders that have been started )
- Tests for cycle time per order (`CycleTimePerOrderViewTests`).
- Tests for order retrieval (`OrdersViewTests`).
- Tests for starting an order (`StartOrderViewTests`).
- Tests for delayed orders (`DelayedOrdersViewTests`).
"""

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from datetime import date, datetime, timedelta
from auth_app.models import users
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from django.utils import timezone
from django.test import TestCase
from django.db.models.query import QuerySet
from rest_framework.test import APIClient
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
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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
        # Arrange: Mocking order, order parts, inventory, picklist, and manufacturing list; and authenticating user
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

class InventoryPicklistItemsViewTests(TestCase):
    def setUp(self):
        # Create a client instance and setup url
        self.client = APIClient()
        self.order_id = 123
        self.url = reverse('inventory_picklist_items', kwargs={'order_id': self.order_id})

        # Create a test user
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

        # Create mock instances for Orders and InventoryPicklist
        self.mock_order = MagicMock(spec=Orders)
        self.mock_order.order_id = self.order_id

        self.mock_picklist = MagicMock(spec=InventoryPicklist)
        self.mock_picklist.picklist_id = 456
        self.mock_picklist.order_id = self.order_id

    @patch('orders.models.Orders.objects.get')
    @patch('inventory.models.InventoryPicklist.objects.get')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    # test_get_inventory_picklist_items_success(): Test successful retrieval of picklist items
    def test_get_inventory_picklist_items_success(self, mock_item_filter, mock_picklist_get, mock_order_get):
        # Arrange: Mocking database queries and authenticate user
        mock_order_get.return_value = self.mock_order
        
        mock_picklist_get.return_value = self.mock_picklist
        
        test_time = datetime.now()
        mock_item_filter.return_value.order_by.return_value.values.return_value = [
            {
                'picklist_item_id': 1,
                'location__location': 'A1',
                'location__warehouse_number': 'WH01',
                'sku_color__sku_color': 'SKU001-RED',
                'amount': 5,
                'status': True,
                'item_picked_timestamp': test_time,
                'picked_at': test_time,
                'area': 'Area1',
                'lineup_nb': 'LN001',
                'model_nb': 'MN001',
                'material_type': 'Material1',
                'manually_picked': False,
                'repick': False,
                'repick_reason': None,
                'actual_picked_quantity': 5
            }
        ]

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistItemView
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['picklist_item_id'], 1)
        self.assertEqual(response.data[0]['location'], 'A1')
        self.assertEqual(response.data[0]['department'], 'WH01')
        self.assertEqual(response.data[0]['sku_color'], 'SKU001-RED')
        self.assertEqual(response.data[0]['quantity'], 5)
        self.assertEqual(response.data[0]['status'], True)
        self.assertEqual(response.data[0]['item_picked_timestamp'], test_time)
        self.assertEqual(response.data[0]['picked_at'], test_time)
        self.assertEqual(response.data[0]['area'], 'Area1')
        self.assertEqual(response.data[0]['lineup_nb'], 'LN001')
        self.assertEqual(response.data[0]['model_nb'], 'MN001')
        self.assertEqual(response.data[0]['material_type'], 'Material1')
        self.assertEqual(response.data[0]['manually_picked'], False)
        self.assertEqual(response.data[0]['repick'], False)
        self.assertEqual(response.data[0]['repick_reason'], None)
        self.assertEqual(response.data[0]['actual_picked_quantity'], 5)
    
    @patch('orders.models.Orders.objects.get')
    # test_get_inventory_picklist_order_not_found(): Handle test case when order doesn't exist
    def test_get_inventory_picklist_items_order_not_found(self, mock_order_get):
        # Arrange: Mocking order instance to throw an exception and authenticate user
        mock_order_get.side_effect = Orders.DoesNotExist

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistItemView
        response = self.client.get(self.url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Order not found')

    @patch('orders.models.Orders.objects.get')
    @patch('inventory.models.InventoryPicklist.objects.get')
    # test_get_inventory_picklist_items_picklist_not_found(): Handle test case when picklist doesn't exist
    def test_get_inventory_picklist_items_picklist_not_found(self, mock_picklist_get, mock_order_get):
        # Arrange: Mocking order and picklist instances to throw an exception and authenticate user
        mock_order_get.return_value = self.mock_order
        mock_picklist_get.side_effect = InventoryPicklist.DoesNotExist

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistItemView
        response = self.client.get(self.url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'No picklist found for the given order')
    
    @patch('orders.models.Orders.objects.get')
    @patch('inventory.models.InventoryPicklist.objects.get')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    # test_get_inventory_picklist_items_empty_picklist(): Handle test case when picklist is empty
    def test_get_inventory_picklist_items_empty_picklist(self, mock_item_filter, mock_picklist_get, mock_order_get):
        # Arrange: Mocking database queries and authenticate user
        mock_order_get.return_value = self.mock_order
        
        self.mock_picklist.order_id = None
        self.mock_picklist.save()
        mock_picklist_get.return_value = self.mock_picklist
        
        mock_item_filter.return_value.order_by.return_value.values.return_value = []

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistItemView
        response = self.client.get(self.url)

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    @patch('orders.models.Orders.objects.get')
    # test_get_inventory_picklist_items_database_exception(): Handle test case where database retrieval throws an exception
    def test_get_inventory_picklist_items_database_exception(self, mock_order_get):
        # Arrange: Mocking order instance to throw exception and authenticate user
        mock_order_get.side_effect = Exception("Unexpected error")

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistItemView
        response = self.client.get(self.url)

        # Assert: Check if exception is raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Unexpected error')
    
    # test_get_inventory_picklist_items_unauthenticated(): Test the case where user is unauthenticated
    def test_get_inventory_picklist_items_unauthenticated(self):
        # Act: Make a GET request to InventoryPicklistItemView
        response = self.client.get(self.url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

class InventoryPicklistViewTests(TestCase):
    def setUp(self):
        # Create a client instance and setup url
        self.client = APIClient()
        self.order_id = 123
        self.url = reverse('inventory_picklist')

        # Create a test user
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

    @patch('orders.models.Orders.objects.filter')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    @patch('inventory.models.InventoryPicklist.objects.filter')
    # test_get_inventory_picklists_success(): Test successful retrieval of picklists
    def test_get_inventory_picklists_success(self, mock_picklist_filter, mock_item_filter, mock_order_filter):
        # Arrange: Mocking database queries and authenticate user
        test_date = datetime.now() + timedelta(days=7)
        mock_order_filter.return_value.values.return_value = [
            {'order_id': 1, 'due_date': test_date},
            {'order_id': 2, 'due_date': test_date}
        ]
        
        mock_item_filter.side_effect = [
            MagicMock(exists=MagicMock(return_value=False)),
            MagicMock(exists=MagicMock(return_value=True))
        ]
        
        mock_picklist_filter.return_value.values_list.return_value.first.side_effect = [
            'employee1',
            None      
        ]

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistView
        response = self.client.get(self.url)

        # Assert: Check response status and data, and verify data from orders
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        self.assertEqual(response.data[0]['order_id'], 1)
        self.assertTrue(response.data[0]['already_filled'])
        self.assertEqual(response.data[0]['assigned_to'], 'employee1')
        
        self.assertEqual(response.data[1]['order_id'], 2)
        self.assertFalse(response.data[1]['already_filled'])
        self.assertIsNone(response.data[1]['assigned_to'])

    @patch('orders.models.Orders.objects.filter')
    # test_get_inventory_picklists_empty(): Test when no orders are in progress
    def test_get_inventory_picklists_empty(self, mock_order_filter):
        # Arrange: Mocking database queries to return no orders and authenticate user
        mock_order_filter.return_value.values.return_value = []

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistView
        response = self.client.get(self.url)

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])
    
    @patch('orders.models.Orders.objects.filter')
    # test_get_inventory_picklists_exception(): Test exception handling 
    def test_get_inventory_picklists_exception(self, mock_order_filter):
        # Arrange: Mocking orders instance to raise an exception and authenticate user
        mock_order_filter.side_effect = Exception("Database error")

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistView
        response = self.client.get(self.url)

        # Assert: Check if exception is raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Database error')

    # test_get_inventory_picklists_unauthenticated(): Test picklist retrieval when user is unauthenticated
    def test_get_inventory_picklists_unauthenticated(self):
        # Act: Make a GET request to InventoryPicklistView without authentication
        response = self.client.get(self.url)

        # Assert: Check if exception is raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")
    
    # test_get_inventory_picklists_unauthorized(): Test picklist retrieval when user is authenticated but unauthorized (not admin or manager)
    def test_get_inventory_picklists_unauthorized(self):
        # Arrange: Change user role to 'user' and authenticate
        self.user.role = 'user'
        self.user.save()

        self.client.force_authenticate(self.user)

        # Act: Make a GET request to InventoryPicklistView
        response = self.client.get(self.url)

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

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
        # Arrange: Mocking database cursor and connection, and authenticate user
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
    def test_get_orders_empty_result_set(self, mock_cursor_func):
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
    # test_get_orders_null_start_timestamp_handling(): Test proper handling of NULL start_timestamp values
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

class StartOrderViewTests(TestCase):
    def setUp(self):
        # Create a client instance and setup url
        self.client = APIClient()
        self.order_id = 123
        self.url = reverse('start_order', kwargs={'order_id': self.order_id})

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
        
        # Create a mock order
        self.order = MagicMock(spec=Orders)
        self.order.order_id = self.order_id
        self.order.status = 'Not Started'

    @patch('orders.views.get_object_or_404')
    @patch('orders.views.timezone.now')
    # test_start_order_success(): Test successful order start
    def test_start_order_success(self, mock_now, mock_get_object):
        # Arrange: Mocking timezone and get_object_or_404 functions, and authenticate user
        test_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0))
        mock_now.return_value = test_time
        mock_get_object.return_value = self.order

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to StartOrderView
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()  # Use .json() to access the response content


        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['order_status'], 'In Progress')
        self.assertEqual(response_data['start_timestamp'], test_time.isoformat())
    
    @patch('orders.views.get_object_or_404')
    # test_start_order_already_in_progress(): Test starting an already in-progress order
    def test_start_order_already_in_progress(self, mock_get_object):
        # Arrange: Mocking get_object_or_404 function and authenticate user
        self.order.status = 'In Progress'
        self.order.save()
        mock_get_object.return_value = self.order

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to StartOrderView
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Order is already in progress')

    @patch('orders.views.get_object_or_404')
    # test_start_order_with_null_status(): Test that order with NULL status gets default status
    def test_start_order_with_null_status(self, mock_get_object):
        # Arrange: Mocking get_object_or_404 function and authenticate user
        self.order.status = None
        self.order.save()
        mock_get_object.return_value = self.order

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to StartOrderView
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()

        # Assert: Check response status and data, and that status got updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(self.order.status, 'In Progress')
    
    @patch('orders.views.get_object_or_404')
    # test_start_order_exception_handling(): Test exception handling
    def test_start_order_exception_handling(self, mock_get_object):
        # Arrange: Mocking get_object_or_404 function to raise an exception and authenticate user
        mock_get_object.side_effect = Exception("Test error")
        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to StartOrderView
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Test error')

    # test_start_order_unauthenticated(): Test the case when user is not authenticated
    def test_start_order_unauthenticated(self):
        # Act: Make a POST request to StartOrderView without authentication
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_data['detail'], "Authentication credentials were not provided.")
    
    # test_start_order_unauthorized(): Test the case when user is authenticated but not authorized (not admin or manager)
    def test_start_order_unauthorized(self):
        # Arrange: Change user role to 'user' and authenticate
        self.user.role = 'user'
        self.user.save()

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to StartOrderView
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()

        # Assert: Check if exception was raised
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_data['detail'], "You do not have permission to perform this action.")
    
    @patch('orders.views.get_object_or_404')
    @patch('orders.views.timezone.now')
    # test_timestamp_set_correctly(): Test that timestamp is set correctly
    def test_start_order_timestamp_set_correctly(self, mock_now, mock_get_object):
        # Arrange: Mocking timezone and get_object_or_404 functions, and authenticate user
        test_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0))
        mock_now.return_value = test_time
        mock_get_object.return_value = self.order

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to StartOrderView
        response = self.client.post(self.url, self.order_id, format='json')
        response_data = response.json()

        # Assert: Check response status and data, and that timestamp is set correctly
        self.assertEqual(self.order.start_timestamp, test_time)
        self.assertEqual(response_data['start_timestamp'], test_time.isoformat())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DelayedOrdersViewTests(TestCase):
    def setUp(self):
        # Create a client instance and setup url
        self.client = APIClient()
        self.order_id = 123
        self.url = reverse('delayed_orders')

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

        # Create test data
        delayed_order = {
            'order_id': 123,
            'due_date': datetime(2023, 1, 5).date(),  # 5 days late
            'ship_complete_timestamp': None,
            'start_timestamp': datetime(2023, 1, 1)
        }
        self.test_date = datetime(2023, 1, 10).date()

        # Mock database query retrievals
        self.mock_queryset_success = MagicMock()
        self.mock_queryset_success.values.return_value.filter.return_value = [delayed_order]

        self.mock_queryset_empty = MagicMock()
        self.mock_queryset_empty.values.return_value.filter.return_value = []

        
    @patch('orders.views.timezone.now')
    @patch('orders.models.Orders.objects.all')
    # test_get_delayed_orders_success(): Test successful retrieval of delayed orders
    def test_get_delayed_orders_success(self, mock_orders_all, mock_now):
        # Arrange: Mocking timezone and Orders queryset, and authenticate user
        mock_now.return_value.date.return_value = self.test_date
        mock_orders_all.return_value = self.mock_queryset_success

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to Delayed Orders view
        response = self.client.get(self.url)

        # Assert: Check response status and data, and verify query was correctly constructed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_id'], 123)
        self.assertEqual(response.data[0]['delay'], 5)
    
    @patch('orders.views.timezone.now')
    @patch('orders.models.Orders.objects.all')
    # test_get_delayed_orders_no_orders(): Handle test case when there are no delayed orders
    def test_get_delayed_orders_no_orders(self, mock_orders_all, mock_now):
        # Arrange: Mocking timezone and Orders (empty) queryset, and authenticate user
        mock_now.return_value.date.return_value = self.test_date
        mock_orders_all.return_value = self.mock_queryset_empty

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to Delayed Orders view
        response = self.client.get(self.url)

        # Assert: Check response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    @patch('orders.views.timezone.now')
    @patch('orders.models.Orders.objects.all')
    # test_get_delayed_orders_database_exception(): Handle the test case where an error occurs during database retrieval
    def test_get_delayed_orders_database_exception(self, mock_orders_all, mock_now):
        # Arrange: Mocking timezone and orders to throw an exception, and authenticate user
        mock_now.return_value.date.return_value = datetime(2023, 1, 10).date()
        mock_orders_all.side_effect = Exception("Database error")

        self.client.force_authenticate(user=self.user)

        # Act: Make a POST request to Delayed Orders view
        response = self.client.get(self.url)

        # Assert: Check if exception is raised
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Database error')
    
    # test_get_delayed_orders_unauthenticated(): Handle the test case when unauthenticated user sends a GET request
    def test_get_delayed_orders_unauthenticated(self):
        # Act: Make a POST request to Delayed Orders view
        response = self.client.get(self.url)

        # Assert: Check if exception is raised
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")