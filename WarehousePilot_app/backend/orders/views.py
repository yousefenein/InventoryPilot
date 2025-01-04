from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import JsonResponse
from .models import Orders
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone 


class OrdersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Query to fetch order data
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT order_id, estimated_duration, status, due_date, start_timestamp
                    FROM orders_orders
                """)
                result = cursor.fetchall()

            # Process the result and return as JSON
            inventory_data = [{
                "order_id": row[0],
                "estimated_duration": row[1],
                "status": row[2],
                "due_date": row[3],
                "start_timestamp": row[4] if row[4] else None, 
            } for row in result]

            return Response(inventory_data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class StartOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = get_object_or_404(Orders, order_id=order_id)

            if order.status == 'In Progress':
                return JsonResponse({'status': 'error', 'message': 'Order is already in progress'}, status=400)

            # Update order status and set timestamp
            order.status = 'In Progress'
            order.start_timestamp = timezone.now()  # Use timezone.now() instead of datetime.now()
            order.save()

            # Return success response with the updated order data
            return JsonResponse({
                'status': 'success',  # Overall success of the action
                'order_id': order.order_id,
                'order_status': order.status,  # Changed this from 'status' to 'order_status'
                'start_timestamp': order.start_timestamp.isoformat()  # ISO 8601 formatted timestamp
            })

        except Exception as e:
            # In case of any error, return error details
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
