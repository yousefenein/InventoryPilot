"""
Unit tests for the StaffManufacturingTasksView API endpoint.

This file contains tests to validate the functionality of the
StaffManufacturingTasksView, ensuring:
- Staff users can retrieve tasks they are assigned to.
- Non-staff users are denied access.
- Unauthenticated users are denied access.


"""

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from inventory.models import users, Part
from manufacturingLists.models import ManufacturingTask
from parts.models import Part
from auth_app.models import users
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken


class StaffManufacturingTasksViewTest(APITestCase):

    def setUp(self):
        # Create a staff user
        self.staff_user = users.objects.create_user(
            username="staffuser",
            password="password",
            email="staffuser@example.com",
            role="staff",
            date_of_hire="1990-01-01",
            first_name="Staff",
            last_name="User",
            department="Manufacturing"
        )

        # Create a non-staff user
        self.non_staff_user = users.objects.create_user(
            username="nonstaffuser",
            password="password",
            email="nonstaffuser@example.com",
            role="employee",
            date_of_hire="1990-01-01",
            first_name="NonStaff",
            last_name="User",
            department="Inventory"
        )

        # Create a part
        self.part = Part.objects.create(
            sku_color="Red",
            sku="SKU123",
            description="Test part",
            qty_per_box=10,
            weight=1.5
        )

        # Create manufacturing tasks with timezone-aware datetimes
        self.task1 = ManufacturingTask.objects.create(
            sku_color=self.part,
            qty=100,
            due_date=timezone.now().date() + timedelta(days=5),
            status="nesting",
            nesting_employee=self.staff_user,
            nesting_end_time=timezone.now() + timedelta(days=1)
        )
        self.task2 = ManufacturingTask.objects.create(
            sku_color=self.part,
            qty=50,
            due_date=timezone.now().date() + timedelta(days=10),
            status="cutting",
            cutting_employee=self.staff_user,
            cutting_end_time=timezone.now() + timedelta(days=2)
        )

    def test_staff_user_can_access_tasks(self):
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)

        url = reverse('staff_manufacturing_tasks/')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check task1 details
        task1 = response.data[0]
        self.assertEqual(task1["manufacturing_id"], self.task1.manufacturing_task_id)
        self.assertEqual(task1["qty"], 100)
        self.assertEqual(task1["sku_color"], "Red")
        self.assertEqual(task1["status"], "nesting")

        # Check task2 details
        task2 = response.data[1]
        self.assertEqual(task2["manufacturing_id"], self.task2.manufacturing_task_id)
        self.assertEqual(task2["qty"], 50)
        self.assertEqual(task2["sku_color"], "Red")
        self.assertEqual(task2["status"], "cutting")


    def test_non_staff_user_cannot_access_tasks(self):
        # Authenticate as non-staff user
        self.client.force_authenticate(user=self.non_staff_user)

        url = reverse('staff_manufacturing_tasks/')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Unauthorized: User is not a staff member.")

    def test_unauthenticated_user_cannot_access_tasks(self):
        url = reverse('staff_manufacturing_tasks/')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CompleteManufacturingTaskTestCase(APITestCase):
    def setUp(self):
        # Create a mock staff user
        self.staff_user = users.objects.create_user(
            username="staffuser",
            password="password",
            email="staffuser@example.com",
            role="staff",
            date_of_hire="1990-01-01",
            first_name="Staff",
            last_name="User",
            department="Manufacturing"
        )
        
        # Set up a test Part instance using correct field names
        self.part = Part.objects.create(
            sku_color="TestColor",
            sku="12345",
            old_sku="54321",
            description="A test part for manufacturing",
            qty_per_box=10,
            weight=1.5,
            length=10,
            lbs1400=2.3,
            crate_size="Large",
            image=None  # assuming the image is optional or handled later
        )
        
        # Set up a test ManufacturingTask instance
        self.manufacturing_task = ManufacturingTask.objects.create(
            sku_color=self.part,
            qty=10,
            due_date=timezone.now(),
            status="nesting",  # Starting at nesting
        )

        # JWT token for authentication
        refresh = RefreshToken.for_user(self.staff_user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_complete_manufacturing_task_nesting_to_bending(self):
        """Test task moves from 'nesting' to 'bending'."""
        url = reverse("complete_task", args=[self.manufacturing_task.manufacturing_task_id])

        # Send POST request to complete the task
        response = self.client.post(url, {"task_id": self.manufacturing_task.manufacturing_task_id})
        
        # Reload the task from the database
        self.manufacturing_task.refresh_from_db()

        # Assert that the task status changed to 'bending' and nesting end time was set
        self.assertEqual(self.manufacturing_task.status, "bending")
        self.assertIsNotNone(self.manufacturing_task.nesting_end_time)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Task status updated to bending")

    def test_complete_manufacturing_task_bending_to_cutting(self):
        """Test task moves from 'bending' to 'cutting'."""
        self.manufacturing_task.status = "bending"
        self.manufacturing_task.save()
        
        url = reverse("complete_task", args=[self.manufacturing_task.manufacturing_task_id])

        # Send POST request to complete the task
        response = self.client.post(url, {"task_id": self.manufacturing_task.manufacturing_task_id})
        
        # Reload the task from the database
        self.manufacturing_task.refresh_from_db()

        # Assert that the task status changed to 'cutting' and bending end time was set
        self.assertEqual(self.manufacturing_task.status, "cutting")
        self.assertIsNotNone(self.manufacturing_task.bending_end_time)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Task status updated to cutting")

    def test_task_already_at_production_qa(self):
        """Test task is already at 'production_qa' and cannot move further."""
        self.manufacturing_task.status = "production_qa"
        self.manufacturing_task.save()

        url = reverse("complete_task", args=[self.manufacturing_task.manufacturing_task_id])

        # Send POST request to complete the task
        response = self.client.post(url, {"task_id": self.manufacturing_task.manufacturing_task_id})

        # Assert that the response status is 400 with the appropriate message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Task is already at the Production QA stage!")

    def test_task_not_found(self):
        """Test when the task ID does not exist."""
        url = reverse("complete_task", args=[9999])
        
        # Send POST request with a non-existent task ID
        response = self.client.post(url, {"task_id": 9999})
        
        # Assert that the response status is 500 with an error message
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()["error"], "No ManufacturingTask matches the given query.")
