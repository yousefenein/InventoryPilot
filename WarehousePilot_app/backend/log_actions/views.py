import logging
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.models import InventoryPicklist, InventoryPicklistItem

# Django logger for backend
logger = logging.getLogger('WarehousePilot_app')

# Create your views here.
class InventoryPickingLogging(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
       