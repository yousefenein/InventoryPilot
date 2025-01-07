from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from auth_app.models import users
from .serializers import StaffSerializer
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def home(request):
    return HttpResponse("Hello, World!")

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsManagerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'manager'

class ManageUsersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role in ['admin', 'manager']:
                staffData = users.objects.all()
            else:
                return Response({"error": "Insufficient permissions"}, status=403)
            
            serializer = StaffSerializer(staffData, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ManageUsersView: {str(e)}")
            return Response({"error": str(e)}, status=500)

class AddUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if request.user.role not in ['admin', 'manager']:
                return Response({"error": "Insufficient permissions"}, status=403)

            data = request.data
            if users.objects.filter(email=data['email']).exists():
                return Response({"error": "User with this email already exists"}, status=400)

            user = users.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                role=data['role'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                department=data['department'],
                dob=data['dob']
            )
            return Response({"message": "User created successfully"})
        except Exception as e:
            logger.error(f"Error in AddUserView: {str(e)}")
            return Response({"error": str(e)}, status=500)

class EditUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            logger.debug(f"Attempting to fetch user with user_id: {user_id}")
            user = users.objects.get(user_id=user_id)
            logger.debug(f"Found user: {user.username}")

            # Check permissions
            if request.user.role not in ['admin', 'manager']:
                return Response({"error": "Insufficient permissions"}, status=403)

            serializer = StaffSerializer(user)
            return Response(serializer.data, status=200)
        except users.DoesNotExist:
            logger.error(f"User with user_id {user_id} not found")
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            logger.error(f"Error in EditUserView.get: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)

    def put(self, request, user_id):
        try:
            logger.debug(f"Attempting to update user with user_id: {user_id}")
            user = users.objects.get(user_id=user_id)

            # Check permissions
            if request.user.role not in ['admin', 'manager']:
                return Response({"error": "Insufficient permissions"}, status=403)

            serializer = StaffSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.debug(f"User {user.username} updated successfully")
                return Response({"message": "User updated successfully"}, status=200)
            else:
                logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)
        except users.DoesNotExist:
            logger.error(f"User with user_id {user_id} not found")
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            logger.error(f"Error in EditUserView.put: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)

class DeleteUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        try:
            user = users.objects.get(user_id=user_id)

            # Check permissions
            if request.user.role not in ['admin', 'manager']:
                return Response({"error": "Insufficient permissions"}, status=403)

            user.delete()
            logger.info(f"User with user_id {user_id} deleted successfully")
            return Response({"message": "User deleted successfully"}, status=200)
        except users.DoesNotExist:
            logger.error(f"User with user_id {user_id} not found")
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            logger.error(f"Error in DeleteUserView: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)
