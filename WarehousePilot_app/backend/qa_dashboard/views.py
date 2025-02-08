from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.db.models import Q
import logging


from manufacturingLists.models import ManufacturingTask, QAErrorReport
from inventory.models import InventoryPicklist
from orders.models import Orders

logger = logging.getLogger('WarehousePilot_app')


class QADashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("Viewing QA dashboard")
        return Response({"message": "Hello QA Dashboard! This is a placeholder."})


class QAManufacturingTasksView(APIView):
    """
    Returns the list of manufacturing tasks assigned to the QA user.
    
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            # Check if the user is QA
            if not hasattr(user, "role") or getattr(user, "role", "").lower() != "qa":
                logger.error("Unauthorized access - User is not a QA employee")
                return Response({"error": "Unauthorized: User is not a QA staff member."},
                                status=status.HTTP_403_FORBIDDEN)
            # Get tasks where the user is assigned as production QA or paint QA
            tasks = ManufacturingTask.objects.filter(
                Q(prod_qa_employee_id=user.user_id) |
                Q(paint_qa_employee_id=user.user_id)
            )
            response_data = []
            for task in tasks:
                task_status = task.status.strip().lower() if task.status else ""
                final_qa = "pending" if task_status == "in progress" else ("completed" if task_status == "pick and pack" else "n/a")
                response_data.append({
                    "manufacturing_task_id": task.manufacturing_task_id,
                    "sku_color_id": task.sku_color_id,
                    "qty": task.qty,
                    "due_date": task.due_date,
                    "prod_qa": "completed" if task.prod_qa else "pending",
                    "paint_qa": "completed" if task.paint_qa else "pending",
                    "status": task_status,
                    "final_qa": final_qa,
                })
            logger.info("Successfully retrieved QA tasks for user %s", user.user_id)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error retrieving QA tasks for user %s: %s", user.user_id, str(e))
            return Response({"error": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateQATaskView(APIView):
    """
    Updates the production and paint QA statuses for a manufacturing task.
    When both are "completed", the backend sets the task's status to "in progress".
    
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            prod_qa = request.data.get("prod_qa")  # Expected: "completed" or "pending"
            paint_qa = request.data.get("paint_qa")  # Expected: "completed" or "pending"
            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)
            if prod_qa in ["completed", "pending"]:
                task.prod_qa = (prod_qa == "completed")
            if paint_qa in ["completed", "pending"]:
                task.paint_qa = (paint_qa == "completed")
            # When both QA steps are completed, update status to "in progress"
            if task.prod_qa and task.paint_qa:
                task.status = "in progress"
            else:
                task.status = "in progress"  
            task.save()
            logger.info("QA task %s updated successfully", task_id)
            return Response({"message": "QA task updated successfully."}, status=status.HTTP_200_OK)
        except ManufacturingTask.DoesNotExist:
            logger.error("Task %s not found", task_id)
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error updating task %s: %s", task_id, str(e))
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportQAErrorView(APIView):
    """
    Reports a QA error for a manufacturing task (sets task.status to "error").
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            subject = request.data.get("subject")
            comment = request.data.get("comment")
            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)
            # Mark the task as 'Error'
            task.status = "error"
            task.save()
            QAErrorReport.objects.create(
                manufacturing_task=task,
                subject=subject,
                comment=comment,
                reported_by=request.user
            )
            logger.info("QA error reported for task %s", task_id)
            return Response({"message": "QA error reported."}, status=status.HTTP_200_OK)
        except ManufacturingTask.DoesNotExist:
            logger.error("Task %s not found", task_id)
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error reporting QA error: %s", str(e))
            return Response({"error": "An error occurred while reporting the issue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateQAStatusView(APIView):
    """
    Updates a task's status from "error" to a new valid status (e.g. "in progress").
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            new_status = request.data.get("status")  # e.g., "in progress"
            if not task_id or not new_status:
                logger.error("Missing task_id or status")
                return Response({"error": "Missing task_id or status"}, status=status.HTTP_400_BAD_REQUEST)
            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)
            if task.status.strip().lower() != "error":
                logger.error("Task %s status is not 'error'", task_id)
                return Response({"error": "Task status must be 'error' to update."}, status=status.HTTP_400_BAD_REQUEST)
            task.status = new_status
            task.save()
            logger.info("Task %s status updated to %s", task_id, new_status)
            return Response({"message": f"Task status updated to '{new_status}'."}, status=status.HTTP_200_OK)
        except ManufacturingTask.DoesNotExist:
            logger.error("Task %s not found", task_id)
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error updating task status: %s", str(e))
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QAErrorListView(APIView):
    """
    Retrieves all QA error reports (with related ManufacturingTask info).
    Accessible by QA and Manager roles.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            user_role = getattr(user, "role", "").lower()
             # Allow both QA and Manager
            if user_role not in ["qa", "manager"]:
                logger.error("Unauthorized access to error reports")
                return Response({"error": "Unauthorized: Must be QA or Manager."}, status=status.HTTP_403_FORBIDDEN)
            # Retrieve all QA error reports
            errors = QAErrorReport.objects.select_related("manufacturing_task", "reported_by").all()
            response_data = []
            for error in errors:
                response_data.append({
                    "id": error.id,
                    "subject": error.subject,
                    "comment": error.comment,
                    "created_at": error.created_at.isoformat(),
                    "manufacturing_task_id": error.manufacturing_task.manufacturing_task_id,
                    "task_status": error.manufacturing_task.status,
                    "sku_color_id": getattr(error.manufacturing_task, "sku_color_id", None),
                    "reported_by": getattr(error.reported_by, "username", "N/A"),
                })
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error fetching QA error reports: %s", str(e))
            return Response({"error": "An unexpected error occurred while fetching QA error reports."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResolveQAErrorView(APIView):
    """
    Resolves a QA error report (only Managers can resolve).
    
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_role = getattr(user, "role", "").lower()
            if user_role != "manager":
                logger.error("Unauthorized: Only managers can resolve QA errors.")
                return Response({"error": "Unauthorized: Only managers can resolve QA errors."}, status=status.HTTP_403_FORBIDDEN)
            error_id = request.data.get("error_id")
            if not error_id:
                return Response({"error": "Missing error_id in request."}, status=status.HTTP_400_BAD_REQUEST)
            # Fetch the error report and delete it
            error_report = QAErrorReport.objects.get(id=error_id)
            error_report.delete()
            logger.info("QA error report %s resolved by manager %s.", error_id, user.username)
            return Response({"message": "Error resolved and removed."}, status=status.HTTP_200_OK)
        except QAErrorReport.DoesNotExist:
            logger.error("QAErrorReport with id %s does not exist.", error_id)
            return Response({"error": "QA Error Report not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error resolving QA error: %s", str(e))
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendToPickAndPackView(APIView):
    """
    Final QA: When final QA is performed, this view updates the task's status from "in progress" to "pick and pack".
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            if not task_id:
                return Response({"error": "manufacturing_task_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)
            if task.status.strip().lower() != "in progress":
                return Response({"error": "Task QA is not in progress."}, status=status.HTTP_400_BAD_REQUEST)
            # Update final QA: mark task as "pick and pack"
            task.status = "pick and pack"
            task.save()
            # Dummy order lookup: use the first available Order.(for now will be fixed later)
            order = Orders.objects.first()
            if not order:
                return Response({"error": "No Order available."}, status=status.HTTP_400_BAD_REQUEST)
            picklist, created = InventoryPicklist.objects.get_or_create(
                order_id=order,
                defaults={"status": False}
            )
            logger.info("Task %s marked as 'pick and pack'; InventoryPicklist ID: %s", task_id, picklist.picklist_id)
            return Response({"message": "Task successfully marked as 'pick and pack'.", "picklist_id": picklist.picklist_id}, status=status.HTTP_200_OK)
        except ManufacturingTask.DoesNotExist:
            logger.error("Task %s not found", task_id)
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error sending task %s to final QA: %s", task_id, str(e))
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
