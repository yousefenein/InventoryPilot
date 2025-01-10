from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from manufacturingLists.models import ManufacturingLists

class ManufacturingListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all manufacturing lists with related orders
            manufacturing_lists = ManufacturingLists.objects.select_related('order_id').all()

            # Build response data
            response_data = [
                {
                    "manufacturing_list_id": m_list.manufacturing_list_id,
                    "order_id": m_list.order_id.order_id,  # From related Orders model
                    "status": m_list.status,  # Manufacturing list status
                }
                for m_list in manufacturing_lists
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
