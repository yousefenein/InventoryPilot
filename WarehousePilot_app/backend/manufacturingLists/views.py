# This file defines views for managing manufacturing lists and their items.

# ManufacturingListView: Retrieves all manufacturing lists along with their associated orders and statuses.
# ManufacturingListItemsView: Retrieves all items in a manufacturing list for a given order ID, including details like SKU, quantity, process, and progress.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from manufacturingLists.models import ManufacturingLists
from .models import ManufacturingListItem, Orders, ManufacturingTask
# from auth_app.views import IsAdminUser
# from manager_dashboard.views import IsManagerUser
import logging

logger = logging.getLogger('WarehousePilot_app')

class ManufacturingListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all manufacturing lists with related orders
            manufacturing_lists = ManufacturingLists.objects.select_related('order_id').all()

            # response data
            response_data = [
                {
                    "manufacturing_list_id": m_list.manufacturing_list_id,
                    "order_id": m_list.order_id.order_id,  # From related Orders model
                    "status": m_list.status,  # Manufacturing list status
                }
                for m_list in manufacturing_lists
            ]

            logger.info("Successfully fetched the manufacturing lists %s", ', '.join([str(x.manufacturing_list_id) for x in manufacturing_lists]))
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Failed to retrieve the manufacturing lists (ManufacturingListView)")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ManufacturingListItemsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        try:
            # Fetch the order based on the provided order_id
            order = Orders.objects.get(order_id=order_id)

            # Fetch the manufacturing list associated with the order
            manufacturing_list = ManufacturingLists.objects.get(order_id=order)

            # Fetch manufacturing list items for the given manufacturing list
            manufacturing_list_items = ManufacturingListItem.objects.filter(
                manufacturing_list_id=manufacturing_list.manufacturing_list_id
            ).values(
                'manufacturing_list_item_id',
                'sku_color__sku_color',  # SKU color of the part
                'amount',
                'manufacturing_process',
                'process_progress'
            )

            # Build response data
            response_data = [
                {
                    "manufacturing_list_item_id": item['manufacturing_list_item_id'],
                    "sku_color": item['sku_color__sku_color'],
                    "quantity": item['amount'],
                    "manufacturing_process": item['manufacturing_process'],
                    "process_progress": item['process_progress'],
                }
                for item in manufacturing_list_items
            ]

            logger.info("Successfully fetched items to be manufactured from order %s", order_id)
            return Response(response_data, status=status.HTTP_200_OK)

        except Orders.DoesNotExist:
            logger.error("Order could not be found (ManufacturingListItemsView)")
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ManufacturingLists.DoesNotExist:
            logger.error("No manufacturing list found for the given order (ManufacturingListItemsView)")
            return Response(
                {"error": "No manufacturing list found for the given order"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error("Failed to fetch items to be manufactured from order %s (ManufacturingListItemsView)", order_id)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ManufacturingTaskView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            department = request.query_params.get('department', None)

            if department:
                manufacturing_tasks = ManufacturingTask.objects.filter(status=department)
            else:
                manufacturing_tasks = ManufacturingTask.objects.all()

            response_data = []
            for task in manufacturing_tasks:
                task_data = {
                    "manufacturing_task_id": task.manufacturing_task_id,
                    "sku_color": task.sku_color.sku_color,
                    "qty": task.qty,
                    "due_date": task.due_date,
                    "status": task.status,
                }

                if department == "nesting":
                    task_data.update({
                        "nesting_start_time": task.nesting_start_time,
                        "nesting_end_time": task.nesting_end_time,
                        "nesting_employee": task.nesting_employee.username if task.nesting_employee else None,
                    })
                elif department == "bending":
                    task_data.update({
                        "bending_start_time": task.bending_start_time,
                        "bending_end_time": task.bending_end_time,
                        "bending_employee": task.bending_employee.username if task.bending_employee else None,
                    })
                elif department == "cutting":
                    task_data.update({
                        "cutting_start_time": task.cutting_start_time,
                        "cutting_end_time": task.cutting_end_time,
                        "cutting_employee": task.cutting_employee.username if task.cutting_employee else None,
                    })
                elif department == "welding":
                    task_data.update({
                        "welding_start_time": task.welding_start_time,
                        "welding_end_time": task.welding_end_time,
                        "welding_employee": task.welding_employee.username if task.welding_employee else None,
                    })
                elif department == "painting":
                    task_data.update({
                        "paint_start_time": task.paint_start_time,
                        "paint_end_time": task.paint_end_time,
                        "paint_employee": task.paint_employee.username if task.paint_employee else None,
                    })

                response_data.append(task_data)

            logger.info("Successfully fetched manufacturing tasks for department: %s", department)
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Failed to retrieve the manufacturing tasks (ManufacturingTaskView)")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


