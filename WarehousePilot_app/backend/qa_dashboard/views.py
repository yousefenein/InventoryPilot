from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.db.models import Q
from manufacturingLists.models import ManufacturingTask

class QADashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello QA Dashboard! This is a placeholder."})

class QAManufacturingTasksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            print(f"User type: {type(user)}")  # Debugging line
            print(f"User attributes: {dir(user)}")
            print(f"User role: {getattr(user, 'role', 'No role attribute found')}")

            if not hasattr(user, 'role') or getattr(user, 'role', '').lower() != 'qa':
                return Response({"error": "Unauthorized: User is not a QA staff member."}, status=status.HTTP_403_FORBIDDEN)

            tasks = ManufacturingTask.objects.filter(
                Q(prod_qa_employee_id=user) | Q(paint_qa_employee_id=user),
                status='Pending'
            )

            response_data = []
            for task in tasks:
                response_data.append({
                    "manufacturing_task_id": task.manufacturing_task_id,
                    "sku_color_id": task.sku_color_id,
                    "qty": task.qty,
                    "due_date": task.due_date,
                    "prod_qa": task.prod_qa,
                    "paint_qa": task.paint_qa,
                    "status": task.status,
                })

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MarkQATaskCompleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            step = request.data.get("qa_step")
            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)

            if step == "Production QA":
                task.prod_qa = True
            elif step == "Paint QA":
                task.paint_qa = True

            if task.prod_qa and task.paint_qa:
                task.status = 'Completed'

            task.save()
            return Response({"message": "QA task marked as completed."}, status=status.HTTP_200_OK)
        except ManufacturingTask.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An error occurred while processing."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportQAErrorView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            task_id = request.data.get("manufacturing_task_id")
            task = ManufacturingTask.objects.get(manufacturing_task_id=task_id)
            task.status = 'Error'
            task.save()
            return Response({"message": "QA error reported."}, status=status.HTTP_200_OK)
        except ManufacturingTask.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An error occurred while reporting the issue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


