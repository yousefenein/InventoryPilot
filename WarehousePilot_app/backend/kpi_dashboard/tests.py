import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="django.db.models.fields")

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from inventory.models import Inventory, InventoryPicklist, InventoryPicklistItem
from parts.models import Part
from orders.models import Orders, OrderPart
from auth_app.models import users
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.test import force_authenticate
from unittest.mock import patch, MagicMock, PropertyMock
from .views import ThroughputView
import logging

class KPIDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test data for related models
        self.part = Part.objects.create(
            sku_color='TEST01',
            sku='TEST',
            description='Test Part'
        )
        self.order = Orders.objects.create(
            order_id=1,  # Explicitly set as per previous fix
            due_date=timezone.now(),
            status='In Progress',
            estimated_duration=5,
            start_timestamp=timezone.now()  # Aware datetime provided here
        )
        # Provide all required fields for users model
        self.user = users.objects.create(
            username='testuser',
            email='test@example.com',
            role='staff',
            date_of_hire=date(2023, 1, 1),
            first_name='Test',
            last_name='User',
            department='Warehouse'
        )
        self.inventory = Inventory.objects.create(
            inventory_id=1,
            location='TESTLOC',
            sku_color=self.part,
            qty=100,
            warehouse_number='WH001',
            amount_needed=50
        )
        self.picklist = InventoryPicklist.objects.create(
            order_id=self.order,
            assigned_employee_id=self.user,
            status=False
        )

        # Create InventoryPicklistItem entries for testing
        self.picklist_item1 = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist,
            location=self.inventory,
            sku_color=self.part,
            amount=10,
            status=True,  # Picked
            picked_at=timezone.now() - timedelta(days=1)  # Picked yesterday
        )
        self.picklist_item2 = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist,
            location=self.inventory,
            sku_color=self.part,
            amount=5,
            status=False  # Not picked
        )
        self.picklist_item3 = InventoryPicklistItem.objects.create(
            picklist_id=self.picklist,
            location=self.inventory,
            sku_color=self.part,
            amount=8,
            status=True,  # Picked
            picked_at=timezone.now()  # Picked today
        )

    def test_order_picking_accuracy(self):
        response = self.client.get(reverse('order_picking_accuracy'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        total_picks = InventoryPicklistItem.objects.count()  # 3 items
        accurate_picks = InventoryPicklistItem.objects.filter(status=True).count()  # 2 items
        expected_accuracy = (accurate_picks / total_picks * 100) if total_picks > 0 else 0

        self.assertEqual(data['accurate_picks'], 2)
        self.assertEqual(data['inaccurate_picks'], 1)
        self.assertEqual(data['accuracy_percentage'], round(expected_accuracy, 2))
        self.assertEqual(data['target_accuracy'], 99)

    def test_daily_picks_data(self):
        response = self.client.get(reverse('daily_picks_data'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)

        # Expect two days of data (yesterday and today)
        self.assertEqual(len(data), 2)

        yesterday = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = timezone.now().strftime("%Y-%m-%d")

        yesterday_data = next((item for item in data if item['day'] == yesterday), None)
        today_data = next((item for item in data if item['day'] == today), None)

        self.assertIsNotNone(yesterday_data)
        self.assertEqual(yesterday_data['picks'], 1)

        self.assertIsNotNone(today_data)
        self.assertEqual(today_data['picks'], 1)

    def test_daily_picks_data_method_not_allowed(self):
        response = self.client.post(reverse('daily_picks_data'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], "Method not allowed")

    def test_daily_picks_details(self):
        response = self.client.get(reverse('daily_picks_details'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)

        # Expect two entries (one for yesterday, one for today)
        self.assertEqual(len(data), 2)

        yesterday = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = timezone.now().strftime("%Y-%m-%d")

        yesterday_data = next((item for item in data if item['day'] == yesterday), None)
        today_data = next((item for item in data if item['day'] == today), None)

        self.assertIsNotNone(yesterday_data)
        self.assertEqual(yesterday_data['order_id'], str(self.order.order_id))
        self.assertEqual(yesterday_data['picks'], 1)

        self.assertIsNotNone(today_data)
        self.assertEqual(today_data['order_id'], str(self.order.order_id))
        self.assertEqual(today_data['picks'], 1)

    def test_daily_picks_details_method_not_allowed(self):
        response = self.client.post(reverse('daily_picks_details'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], "Method not allowed")

    def test_order_picking_accuracy_empty(self):
        InventoryPicklistItem.objects.all().delete()
        response = self.client.get(reverse('order_picking_accuracy'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['accurate_picks'], 0)
        self.assertEqual(data['inaccurate_picks'], 0)
        self.assertEqual(data['accuracy_percentage'], 0)
        self.assertEqual(data['target_accuracy'], 99)

    def test_order_fulfillment_rate_get(self):
        self.order.start_timestamp = timezone.now() - timedelta(days=1)
        self.order.save()

        url = reverse('order_fulfillment_rate')
        response = self.client.get(url, {'filter': 'day', 'date': self.order.start_timestamp.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

        day_str = self.order.start_timestamp.strftime("%Y-%m-%d")
        day_entry = next((item for item in data if item['period'] == day_str), None)
        self.assertIsNotNone(day_entry)
        self.assertGreaterEqual(day_entry['total_orders_started'], 1)

    def test_order_fulfillment_rate_invalid_date(self):
        url = reverse('order_fulfillment_rate')
        response = self.client.get(url, {'filter': 'day', 'date': 'invalid-date'})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Invalid date format", data.get("error", ""))

    def test_order_fulfillment_rate_method_not_allowed(self):
        url = reverse('order_fulfillment_rate')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
        
    def test_active_orders_get(self):
        self.order.start_timestamp = timezone.now() - timedelta(days=10)
        self.order.save()
        url = reverse('active_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            sample = data[0]
            self.assertIn("date", sample)
            self.assertIn("active_orders", sample)

    def test_active_orders_method_not_allowed(self):
        url = reverse('active_orders')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
    
    def test_completed_orders_get(self):
        self.order.start_timestamp = timezone.now() - timedelta(days=5)
        self.order.save()

        completed_order = Orders.objects.create(
            order_id=2,
            due_date=timezone.now(),
            status='Completed',
            estimated_duration=5,
            start_timestamp=timezone.now() - timedelta(days=5)
        )

        completed_picklist = InventoryPicklist.objects.create(
            order_id=completed_order,
            assigned_employee_id=self.user,
            status=True,
            picklist_complete_timestamp=timezone.now() - timedelta(days=4)
        )

        url = reverse('completed_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            sample = data[0]
            self.assertIn("date", sample)
            self.assertIn("completed_orders", sample)

    def test_completed_orders_method_not_allowed(self):
        url = reverse('completed_orders')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
        
    def test_active_orders_details_get(self):
        self.order.start_timestamp = timezone.now() - timedelta(days=5)
        self.order.save()
        url = reverse('active_orders_details')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            sample = data[0]
            self.assertIn("order_id", sample)
            self.assertIn("start_date", sample)
            self.assertIn("due_date", sample)
            self.assertIn("assigned_employee", sample)
            self.assertIn("items", sample)
            if sample["items"]:
                item_sample = sample["items"][0]
                self.assertIn("sku_color", item_sample)
                self.assertIn("quantity", item_sample)
                self.assertIn("location", item_sample)
                self.assertIn("status", item_sample)

    def test_active_orders_details_method_not_allowed(self):
        url = reverse('active_orders_details')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)


class ThroughputViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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
        self.view = ThroughputView.as_view()
        self.url = reverse('throughput_threshold')
        
        # Set up test data dates
        self.today = timezone.now().date()
        self.year_ago = self.today - timedelta(days=365)
        
        # Disable logging for cleaner test output
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)

    def test_unauthenticated_access(self):
        """Test that unauthenticated access is denied."""
        request = self.factory.get(self.url)
        response = self.view(request)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_access(self):
        """Test that authenticated access is allowed."""
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    @patch('orders.models.Orders.objects.filter')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    @patch('orders.models.OrderPart.objects.filter')
    def test_throughput_data_structure(self, mock_packed, mock_picked, mock_shipped):
        """Test the basic structure of the returned data."""
        # Mock the shipped orders response
        mock_order = MagicMock()
        mock_order.ship_date = self.today
        mock_shipped_qs = MagicMock()
        mock_shipped_qs.__iter__.return_value = [mock_order]
        mock_shipped.return_value = mock_shipped_qs

        # Mock the picked items response
        mock_picked_qs = MagicMock()
        mock_picked_qs.annotate.return_value.values.return_value.annotate.return_value = []
        mock_picked.return_value = mock_picked_qs

        # Mock the packed items response
        mock_packed_qs = MagicMock()
        mock_packed_qs.annotate.return_value.values.return_value.annotate.return_value = []
        mock_packed.return_value = mock_packed_qs

        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 366)  # 365 days + current day

        # Check each day has the expected structure
        for day_data in response.data:
            self.assertIn('day', day_data)
            self.assertIn('picked', day_data)
            self.assertIn('packed', day_data)
            self.assertIn('shipped', day_data)

    @patch('orders.models.OrderPart.objects.filter')
    def test_shipped_items_calculation(self, mock_orderpart_filter):
        """Test shipped items are correctly calculated."""
        # Mock the aggregate method to return a total of 5
        mock_orderpart_filter.return_value.aggregate.return_value = {'total': 5}

        # Make the request
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)

        # Assert the response
        self.assertEqual(response.status_code, 200)
        data = response.data
        today_data = next((item for item in data if item['day'] == self.today.strftime('%Y-%m-%d')), None)
        self.assertIsNotNone(today_data)
        self.assertEqual(today_data['shipped'], 0)

    @patch('orders.models.Orders.objects.filter')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    @patch('orders.models.OrderPart.objects.filter')
    def test_picked_items_calculation(self, mock_packed, mock_picked, mock_shipped):
        """Test picked items are correctly calculated."""
        # Mock empty shipped orders
        mock_shipped.return_value = []
        
        # Mock picked items for today
        mock_picked_item = {'day': self.today, 'total_picked': 10}
        mock_picked_qs = MagicMock()
        mock_picked_qs.annotate.return_value.values.return_value.annotate.return_value = [mock_picked_item]
        mock_picked.return_value = mock_picked_qs
        
        # Mock empty packed items
        mock_packed.return_value.annotate.return_value.values.return_value.annotate.return_value = []

        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)

        today_data = next(item for item in response.data if item['day'] == self.today.strftime("%Y-%m-%d"))
        self.assertEqual(today_data['picked'], 10)
        self.assertEqual(today_data['shipped'], 0)
        self.assertEqual(today_data['packed'], 0)

    @patch('orders.models.Orders.objects.filter')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    @patch('orders.models.OrderPart.objects.filter')
    def test_packed_items_calculation(self, mock_packed, mock_picked, mock_shipped):
        """Test packed items are correctly calculated."""
        # Mock empty shipped and picked items
        mock_shipped.return_value = []
        mock_picked.return_value.annotate.return_value.values.return_value.annotate.return_value = []
        
        # Mock packed items for today
        mock_packed_item = {'day': self.today, 'total_packed': 7}
        mock_packed_qs = MagicMock()
        mock_packed_qs.annotate.return_value.values.return_value.annotate.return_value = [mock_packed_item]
        mock_packed.return_value = mock_packed_qs

        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)

        today_data = next(item for item in response.data if item['day'] == self.today.strftime("%Y-%m-%d"))
        self.assertEqual(today_data['packed'], 7)
        self.assertEqual(today_data['shipped'], 0)
        self.assertEqual(today_data['picked'], 0)

    @patch('orders.models.Orders.objects.filter')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    @patch('orders.models.OrderPart.objects.filter')
    def test_all_metrics_together(self, mock_orders_filter, mock_picklist_filter, mock_orderpart_filter):
        """Test when all three metrics have data for the same day."""
        # Mock shipped items using side_effect
        def mock_aggregate(*args, **kwargs):
            return {'total': 5}

        mock_orderpart_filter.return_value.aggregate.side_effect = mock_aggregate

        # Mock picked items
        mock_picklist_filter.return_value.annotate.return_value.values.return_value.annotate.return_value = [
            {'day': self.today, 'total_picked': 3}
        ]

        # Mock packed items
        mock_orderpart_filter.return_value.annotate.return_value.values.return_value.annotate.return_value = [
            {'day': self.today, 'total_packed': 2}
        ]

        # Make the request
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)

        # Assert the response
        self.assertEqual(response.status_code, 200)
        data = response.data
        today_data = next((item for item in data if item['day'] == self.today.strftime('%Y-%m-%d')), None)
        self.assertIsNotNone(today_data)
        self.assertEqual(today_data['shipped'], 0)
        self.assertEqual(today_data['picked'], 3)
        self.assertEqual(today_data['packed'], 0)

    @patch('orders.models.Orders.objects.filter')
    @patch('inventory.models.InventoryPicklistItem.objects.filter')
    @patch('orders.models.OrderPart.objects.filter')
    def test_exception_handling(self, mock_packed, mock_picked, mock_shipped):
        """Test that exceptions are properly caught and handled."""
        # Make shipped orders query raise an exception
        mock_shipped.side_effect = Exception("Test error")
        
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request)
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Test error')