# This file defines authentication and user management endpoints.

# LoginView: Handles user authentication and returns JWT tokens.
# ChangePasswordView: Allows authenticated users to update their password.
# ProfileView: Retrieves profile details of the currently authenticated user.
# RetrieveUsers: Fetches a list of all users from the database.
# ThemePreferenceView: Manages the theme preference of the user (light or dark mode)
# PasswordResetRequestView: Initiates the password reset process by sending an email with a reset link.
# PasswordResetView: Completes the password reset process using the token and new password provided by the user.

from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import users
from django.contrib.auth import update_session_auth_hash
from .serializers import StaffSerializer, PasswordResetRequestSerializer, PasswordResetSerializer
import logging
from django_ratelimit.decorators import ratelimit

# Django logger for backend
logger = logging.getLogger('WarehousePilot_app')

@method_decorator(ratelimit(key='ip',rate='5/m',method='POST',block=False), name='post')
class LoginView(APIView):
    permission_classes = []

    def post(self, request):
            username = request.data.get("username")
            password = request.data.get("password")

            logger.debug("Login user data - Username: %s", username)

            # Django built-in authentication
            user = authenticate(username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                logger.info(f"User {username} successfully logged in")
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'username': user.username,
                        'role': user.role,
                        'date_of_hire': user.date_of_hire,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'department': user.department
                    }
                })
            else:
                # Check if this request is beyond allowed attempts
                if getattr(request, 'limited', False):
                    # The IP address has exceeded 5 failed attempts this minute
                    return Response(
                        {"detail": "Too many failed login attempts. Please try again later."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                else:
                    return Response(
                        {"detail": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
# This is the view for the change password endpoint           
class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        username = request.data.get("username")
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            logger.error(f"User {user}'s old password provided for password reset was incorrect")
            return Response({"detail": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user) # to keep the user logged in after changing the password

        logger.info(f"User {user} successfully changed their password.")
        return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)

# This is the view for the profile endpoint, gets your profile information    
class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            logger.debug(f"Profile (fetched data) - Request user: {user}")
            logger.debug(f"Profile (fetched data) - User type: {type(user)}")

            user_data = {
                'username': user.username,
                'email': user.email,
                'role': getattr(user, 'role', 'N/A'),  
                'first_name': getattr(user, 'first_name', 'N/A'),
                'last_name': getattr(user, 'last_name', 'N/A'),
                'department': getattr(user, 'department', 'N/A'),
                'theme_preference': getattr(user, 'theme_preference', 'light')
            }
            logger.info(f"Fetched the profile of the user {user.username}")
            return Response(user_data)
        except Exception as e:
            logger.error("Failed to retrieve user data in Profile")
            return Response({"error": str(e)}, status=500)
        
class RetrieveUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            staffData = users.objects.all()
            serializer = StaffSerializer(staffData, many=True)
            if serializer.data is not None:
                logger.info("Retrieved data for all users (auth)")
            return Response(serializer.data)
        except Exception as e:
            logger.error("Failed to retrieve all users data from the database (auth)")
            return Response({"error": str(e)}, status=500)

class ThemePreferenceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the current user's theme preference"""
        user = request.user
        return Response({"theme_preference": user.theme_preference}, status=status.HTTP_200_OK)

    def post(self, request):
        """Update the user's theme preference"""
        theme = request.data.get("theme")
        if theme not in ['light', 'dark']:
            return Response(
                {"error": "Invalid theme choice. Please select 'light' or 'dark'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.theme_preference = theme
        user.save()

        logger.info(f"User {user.username} successfully updated their theme preference to {theme}.")
        return Response({"detail": f"Theme preference updated to {theme}"}, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data.get("email"))
        email = request.data.get("email")

        # Check if the email is valid
        validated_email = serializer.validate_email(email)

        # Generate the password reset token and send the email
        serializer.send_reset_email(validated_email)

        return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        # Validate the token and user id from link
        validated_user = serializer.validate_token(request.data)
        new_password = request.data.get("new_password")

        # Sets the new password for the user
        serializer.set_new_password(validated_user, new_password)
        return Response({"detail": "Password has been reset successfully."})