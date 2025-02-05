from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.db.models import Q
from manufacturingLists.models import ManufacturingTask, QAErrorReport
import logging

logger = logging.getLogger('WarehousePilot_app')


class QADashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("Viewing QA dashboard")
        return Response({"message": "Hello QA Dashboard! This is a placeholder."})


class QAManufacturingTasksView(APIView):
    """
    Fetches manufacturing tasks assigned to the QA user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            logger.debug(f"User type: {type(user)}")
            logger.debug(f"User attributes: {dir(user)}")
            logger.debug(f"User role: {getattr(user, 'role', 'No role attribute found')}")
            logger.debug(f"User ID: {user.user_id}")

            # Check if the user is QA
            if not hasattr(user, 'role') or getattr(user, 'role', '').lower() != 'qa':
                logger.error("Unauthorized access - User is not a QA employee (QAManufacturingTasksView)")
                return Response({"error": "Unauthorized: User is not a QA staff member."},
                                status=status.HTTP_403_FORBIDDEN)

            # Get tasks where the user is assigned as production QA or paint QA
            tasks = ManufacturingTask.objects.filter(
                Q(prod_qa_employee_id=user.user_id) |
                Q(paint_qa_employee_id=user.user_id)
            )

            response_data = []
            for task in tasks:
                response_data.append({
                    "manufacturing_task_id": task.manufacturing_task_id,
                    "sku_color_id": task.sku_color_id,
                    "qty": task.qty,
                    "due_date": task.due_date,
                    "prod_qa": "Completed" if task.prod_qa else "Pending",
                    "paint_qa": "Completed" if task.paint_qa else "Pending",
                    "status": task.status,
                })

            logger.info("Successfully retrieved all tasks associated with QA staff member %s", user.user_id)
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Failed to retrieve task associated with QA staff member %s. Error: %s", user.user_id, str(e))
            return Response({"error": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateQATaskView(APIView):
    """
    Allows a QA user to update the QA status of a manufacturing task
    (prod_qa or paint_qa to 'Completed' or 'Pending').
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("Received data:", request.data)
            task_id = request.data.get("manufacturing_task_id")
            prod_qa = request.data.get("prod_qa")     # "Completed" or "Pending"
            paint_qa = request.data.get("paint_qa")  # "Completed" or "Pending"

            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)

            # Update booleans if provided
            if prod_qa in ["Completed", "Pending"]:
                task.prod_qa = (prod_qa == "Completed")

            if paint_qa in ["Completed", "Pending"]:
                task.paint_qa = (paint_qa == "Completed")

            # If both QA steps are completed, set status to Completed; otherwise In Progress
            if task.prod_qa and task.paint_qa:
                task.status = 'Completed'
            else:
                task.status = 'In Progress'

            task.save()

            logger.info("QA task %s status has been updated successfully", task_id)
            return Response({"message": "QA task updated successfully."},
                            status=status.HTTP_200_OK)

        except ManufacturingTask.DoesNotExist:
            logger.error("Manufacturing task %s could not be found (UpdateQATaskView)", task_id)
            return Response({"error": "Task not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Failed to update status of manufacturing task %s (UpdateQATaskView): %s", task_id, str(e))
            return Response({"error": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportQAErrorView(APIView):
    """
    Allows a QA user to report a QA error for a manufacturing task (sets task.status to 'Error').
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            subject = request.data.get("subject")  # new fields
            comment = request.data.get("comment")

            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)

            # Mark the task as 'Error'
            task.status = 'Error'
            task.save()

            QAErrorReport.objects.create(
                manufacturing_task=task,
                subject=subject,
                comment=comment,
                reported_by=request.user
            )

            logger.info("QA report for task %s has been created", task_id)
            return Response({"message": "QA error reported."}, status=status.HTTP_200_OK)

        except ManufacturingTask.DoesNotExist:
            logger.error("Manufacturing task %s could not be found (ReportQAErrorView)", task_id)
            return Response({"error": "Task not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error while reporting QA issue: {str(e)}")
            return Response({"error": "An error occurred while reporting the issue."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateQAStatusView(APIView):
    """
    Allows a QA user to update a task from 'Error' back to 'In Progress' (or another status).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            new_status = request.data.get("status")  # Expected to be "In Progress"

            if not task_id or not new_status:
                logger.error("Missing task_id or status from update QA status (UpdateQAStatusView)")
                return Response({"error": "Missing task_id or status"},
                                status=status.HTTP_400_BAD_REQUEST)

            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)

            # Ensure the current status is 'Error' before allowing the update
            if task.status != 'Error':
                logger.error("Task status must be 'Error' to update (UpdateQAStatusView)")
                return Response({"error": "Task status must be 'Error' to update."},
                                status=status.HTTP_400_BAD_REQUEST)

            task.status = new_status  # Update the status
            task.save()

            logger.info("Task status has been updated to %s", new_status)
            return Response({"message": f"Task status updated to '{new_status}'."},
                            status=status.HTTP_200_OK)

        except ManufacturingTask.DoesNotExist:
            logger.error("Manufacturing task does not exist (UpdateQAStatusView)")
            return Response({"error": "Task not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Failed to update manufacturing task status (UpdateQAStatusView): %s", str(e))
            return Response({"error": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QAErrorListView(APIView):
    """
    Retrieves a list of all QAErrorReport entries (and related ManufacturingTask info).
    Accessible by QA staff and managers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            user_role = getattr(user, 'role', '').lower()

            # Allow both QA and Manager
            if user_role not in ['qa', 'manager']:
                logger.error("Unauthorized access - User is neither QA nor Manager (QAErrorListView)")
                return Response(
                    {"error": "Unauthorized: User must be QA or a Manager."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Retrieve all QA error reports
            errors = QAErrorReport.objects.select_related('manufacturing_task', 'reported_by').all()

            response_data = []
            for error in errors:
                response_data.append({
                    "id": error.id,
                    "subject": error.subject,
                    "comment": error.comment,
                    "created_at": error.created_at.isoformat(),
                    "manufacturing_task_id": error.manufacturing_task.manufacturing_task_id,
                    "task_status": error.manufacturing_task.status,
                    "sku_color_id": getattr(error.manufacturing_task, 'sku_color_id', None),
                    "reported_by": getattr(error.reported_by, 'username', 'N/A'),
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to retrieve QA error reports: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred while fetching QA error reports."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResolveQAErrorView(APIView):
    """
    Allows a Manager to 'resolve' an error by removing it from the QAErrorReport table.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_role = getattr(user, 'role', '').lower()
            
            # Only Managers can remove errors
            if user_role != 'manager':
                logger.error("Unauthorized access - Only managers can resolve QA errors.")
                return Response({"error": "Unauthorized: Only managers can resolve QA errors."},
                                status=status.HTTP_403_FORBIDDEN)

            error_id = request.data.get("error_id")
            if not error_id:
                return Response({"error": "Missing error_id in request."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Fetch the error report and delete it
            error_report = QAErrorReport.objects.get(id=error_id)
            error_report.delete()

            logger.info(f"QA error report {error_id} resolved and removed by manager {user.username}.")
            return Response({"message": "Error resolved and removed."}, status=status.HTTP_200_OK)
        
        except QAErrorReport.DoesNotExist:
            logger.error(f"QAErrorReport with id {error_id} does not exist.")
            return Response({"error": "QA Error Report not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to resolve QA Error: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
