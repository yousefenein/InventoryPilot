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
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        # Initialize the list of picklist items
        picked_items = []

        try:
            # Fetch all the picklists
            picklists = InventoryPicklist.objects.all().values('picklist_id', 'warehouse_nb', 'assigned_employee_id')

            try:
                for picklist in picklists:
                    logger.info(f"Picklist: {picklist}")
                    # Set the values for the following variables
                    id = picklist['picklist_id']
                    warehouse = picklist['warehouse_nb']
                    employee_id = picklist['assigned_employee_id']
                    logger.info(f"Picklist ID: {id}, Warehouse: {warehouse}, Employee ID: {employee_id}")

                    # Fetch all the picklist items for each picklist
                    picklist_items = InventoryPicklistItem.objects.filter(picklist_id=id).values('item_picked_timestamp', 'location', 'sku_color', 'amount')

                    # Loop through each picklist item
                    for item in picklist_items:
                        picked_items.append({
                            'warehouse': warehouse,
                            'date': item['item_picked_timestamp'].date(),
                            'time': item['item_picked_timestamp'],
                            'employee_id': employee_id,
                            'transaction_type': 'Picking',
                            'sku_color': item['sku_color'],
                            'location': item['location'],
                            'qty_out': item['amount']
                        })
                
                # Sort the list of picklist items by date annd time in descending order
                picked_items.sort(key=lambda x: x['time'], reverse=True)

                logger.info(f"Inventory Picking Logging: {picked_items}")
                return Response(picked_items)
            
            except Exception as e:
                logger.error("Failed to get info on the individual picklist (InventoryPickingLogging)")
                return Response({"error": str(e)}, status=500)
            
        except InventoryPicklist.DoesNotExist:
            logger.error("Inventory Picklist does not exist")
            return Response(status=404)
        
        except InventoryPicklistItem.DoesNotExist:
            logger.error("Inventory Picklist Item does not exist")
            return Response(status=404)
        
        except Exception as e:
            logger.error("Failed to fetch data tracking inventory picking (InventoryPickingLogging)")
            return Response({"error": str(e)}, status=500)