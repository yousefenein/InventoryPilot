from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import users
from django.contrib.auth import update_session_auth_hash
from .serializers import StaffSerializer

# Custom Permissions
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class IsManagerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_manager

# This is the view for the login endpoint
class LoginView(APIView):
    permission_classes = []

    def post(self, request):
            username = request.data.get("username")
            password = request.data.get("password")

            print(f"Username: {username}")
            print(f"Password: {password}")

            # Django built-in authentication
            user = authenticate(username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'username': user.username,
                        'role': user.role,
                        'dob': user.dob,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'department': user.department
                    }
                })
            else:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# This is the view for the change password endpoint           
class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user) # to keep the user logged in after changing the password

        return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)

# This is the view for the profile endpoint, gets your profile information    
class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            print(f"Request user: {user}")  # Debugging
            print(f"User type: {type(user)}")  # Debugging

            user_data = {
                'username': user.username,
                'email': user.email,
                'role': getattr(user, 'role', 'N/A'),  
                'first_name': getattr(user, 'first_name', 'N/A'),
                'last_name': getattr(user, 'last_name', 'N/A'),
                'department': getattr(user, 'department', 'N/A'),
            }
            return Response(user_data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class RetrieveUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            staffData = users.objects.all()
            serializer = StaffSerializer(staffData, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# New views for role-based access
class AdminDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({"message": "Admin dashboard access granted"})

class ManagerDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsManagerUser]

    def get(self, request):
        return Response({"message": "Manager dashboard access granted"})

class UserManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id):
        user = get_object_or_404(users, user_id=user_id)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_object_or_404(users, user_id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)