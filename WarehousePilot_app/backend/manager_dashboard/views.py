from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from auth_app.models import users

# Create your views here.
def home(request):
    return HttpResponse("Hello, World!")

class IsManagerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'manager'

class ManagerDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsManagerUser]

    def get(self, request):
        return Response({
            "message": "Manager dashboard access granted",
            "user": request.user.username,
            "role": request.user.role
        })