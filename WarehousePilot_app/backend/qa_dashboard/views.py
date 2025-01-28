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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            logger.debug(f"User type: {type(user)}")  # Debugging
            logger.debug(f"User attributes: {dir(user)}")
            logger.debug(f"User role: {getattr(user, 'role', 'No role attribute found')}")
            logger.debug(f"User ID: {user.user_id}")

            # Check if the user is indeed QA
            if not hasattr(user, 'role') or getattr(user, 'role', '').lower() != 'qa':
                logger.error("Unauthorized access - User is not a QA employee (QAManufacturingTasksView)")
                return Response({"error": "Unauthorized: User is not a QA staff member."},
                                status=status.HTTP_403_FORBIDDEN)

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
            logger.error("Failed to retrieve task associated with QA staff member %s", user.user_id)
            return Response({"error": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateQATaskView(APIView):
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

            # If both QA are completed, set status to Completed; otherwise In Progress
            if task.prod_qa and task.paint_qa:
                task.status = 'Completed'
            else:
                task.status = 'In Progress'

            task.save()

            logger.info("QA task %s status has been updated successfully", task_id)
            return Response({"message": "QA task updated successfully."},
                            status=status.HTTP_200_OK)

        except ManufacturingTask.DoesNotExist:
            logger.error("Manufacturing task could not be found (UpdateQATaskView)")
            return Response({"error": "Task not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Failed to update status of manufacturing task %s (UpdateQATaskView)", task_id)
            return Response({"error": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportQAErrorView(APIView):
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            new_status = request.data.get("status")  # Expected to be "In Progress"

            if not task_id or not new_status:
                return Response({"error": "Missing task_id or status"},
                                status=status.HTTP_400_BAD_REQUEST)

            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)

            # Ensure the current status is 'Error' before allowing the update
            if task.status != 'Error':
                return Response({"error": "Task status must be 'Error' to update."},
                                status=status.HTTP_400_BAD_REQUEST)

            task.status = new_status  # Update the status
            task.save()

            return Response({"message": f"Task status updated to '{new_status}'."},
                            status=status.HTTP_200_OK)

        except ManufacturingTask.DoesNotExist:
            return Response({"error": "Task not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

