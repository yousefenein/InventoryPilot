# This file defines views for managing orders, picklists, and manufacturing lists.

# GenerateInventoryAndManufacturingListsView: Generates inventory picklists and manufacturing lists when an order is started.
# OrdersView: Retrieves all order data including status, due date, and timestamps.
# StartOrderView: Updates an order's status to 'In Progress' and sets the start timestamp.
# InventoryPicklistView: Retrieves picklists for orders in progress, indicating if they are filled and their assigned employee.
# InventoryPicklistItemsView: Fetches detailed items of a picklist for a given order, including location, SKU, quantity, and status.


from django.shortcuts import get_object_or_404
from datetime import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from .models import Orders, OrderPart
from inventory.models import Inventory, InventoryPicklist, InventoryPicklistItem
from parts.models import Part
from manufacturingLists.models import ManufacturingLists, ManufacturingListItem
from django.db.models import Sum
from django.db.models import Q
from rest_framework import status

from django.http import JsonResponse
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone 

from django.shortcuts import get_object_or_404
from datetime import datetime
from django.utils import timezone 

import logging

logger = logging.getLogger('WarehousePilot_app')

#generates an inventory picklist and a maufacturing list of an order once the order is "started"
# Note: print statements have been commented out and can be uncommented for debugging if needed
class GenerateInventoryAndManufacturingListsView(APIView):
    def post(self, request):
        #retrieve the order id from the http request
        orderID = request.data.get("orderID")
        logger.debug("GenerateInventoryAndManufacturingListsView\nOrder ID: %s", orderID)
        #retrieve the order object from the database using the order id
        order = Orders.objects.get(order_id=orderID)
        logger.debug("Retrieved order: %s", order.__dict__)
        
        #get all the parts of the order
        orderParts = OrderPart.objects.filter(order_id=order)
        #'''
        logger.debug("Order parts: %s", ', '.join([str(x.order_part_id) for x in orderParts]))
        #'''
        #get a list of the UNIQUE sku_colors from the parts in the order
        #***
        orderPartSkuColor = list(set(orderParts.values_list('sku_color', flat=True)))
        #'''
        logger.debug("Unique Order Parts SKU COLORS: %s", ', '.join([str(x) for x in orderPartSkuColor]))
        #'''
        #get all the objects in inventory that have a quantity greater than 0, amount needed equal to 0 and match the sku_colors of the parts in the order
        inventory = Inventory.objects.filter(sku_color__in=orderPartSkuColor, qty__gt = 0, amount_needed = 0)
        #'''
        logger.debug("Matching parts in inventory with a quantity greater than 0: %s", ', '.join([str(x) for x in inventory]))
        logger.debug("Inventory count: %s", inventory.count())
        #'''
        if inventory.exists() == True: #if there were matching objects in inventory
            logger.debug("ENTER 1st IF BLOCK")
            #find all the unique skus in the matching inventory objects, since there can be more than one object in inventory with the same sku
            inventorySkus = set(list(inventory.values_list("sku_color", flat=True)))
            logger.debug(f"inventory matching skus: {inventorySkus}")
            #create an inventory picklist for the order
            inventoryPicklist = InventoryPicklist.objects.create(status = False, order_id=order)
            # create a list of picklist items
            manufacturingList= ManufacturingLists(order_id=order, status='Pending')
            inventoryPicklistItems = []
            manuListItems = []
            for s in inventorySkus: #loop through the unique matching inventory sku set
                # find the total of the quantity of each unique sku in inventory, aggregating all the inventory objects with the same sku together
                totalInventoryQty = Inventory.objects.filter(sku_color=Part.objects.get(sku_color=s)).aggregate(total=Sum('qty'))['total']
                logger.debug(f"total inventory qty: {totalInventoryQty}")
                ##orderQty = OrderPart.objects.get(order_id=order, sku_color=s).__getattribute__("qty")
                orderQty = OrderPart.objects.filter(order_id=order, sku_color=s).aggregate(total=Sum('qty'))['total']
                logger.debug(f"total order qty: {orderQty}")

                #if inventory amount exceeds needed amount, only the needed amount will be chosen, and if needed amount exceeds available amount, only the available amount is chosen
                manuListItemQty = 0
                if orderQty <= totalInventoryQty:
                    picklistQty = orderQty
                    logger.debug(f"picklist qty: {picklistQty}")
                else: #amount needed exceeds amount available in inventory
                    picklistQty = totalInventoryQty
                    logger.debug(f"picklist qty: {picklistQty}")
                    #create a manufacturing list item with the remaining amount needed for the order
                    manuListItemQty = orderQty - picklistQty
                    logger.debug(f"manuList qty: {manuListItemQty}")
                    manuListItems.append(ManufacturingListItem(manufacturing_list_id=manufacturingList, sku_color=Part.objects.get(sku_color=s), amount=manuListItemQty))
                    for x in Inventory.objects.filter(sku_color=s):
                        x.amount_needed=manuListItemQty
                        x.save()

                #add the picklist item with the appropriate amount to the list of inventory picklist items
                inventoryPicklistItems.append(InventoryPicklistItem(picklist_id = inventoryPicklist, sku_color=Part.objects.get(sku_color=s), amount = picklistQty, status = False))
            #bulk create all the inventory picklist items in the database
            InventoryPicklistItem.objects.bulk_create(inventoryPicklistItems)
            #'''
            logger.debug("All Picklist Items: %s", ', '.join([str(x) for x in InventoryPicklistItem.objects.filter(picklist_id=inventoryPicklist)]))
            #'''
            if len(manuListItems) > 0:
                logger.debug("**Creating manufacturing list 1st if block")
                manufacturingList.save()
                ManufacturingListItem.objects.bulk_create(manuListItems)
                
        logger.debug(f"orderPartSkuColor): {orderPartSkuColor}")
        logger.debug(f"orderPartSkuColor len: {len(orderPartSkuColor)}")
        invSkuLen = len(set(list(inventory.values_list("sku_color", flat=True))))
        logger.debug(f"matching inventory sku len): {invSkuLen}")
        #if not all the parts in the order matched with the parts in inventory, then we have remaining parts that need to be in the manufacturing list
        if inventory.exists() == False or (len((set(orderPartSkuColor)) - set(list(inventory.values_list("sku_color", flat=True)))) > 0):
            logger.debug("ENTER 2nd IF BLOCK")
            invSkuLen = len(set(list(inventory.values_list("sku_color", flat=True))))
            logger.debug(f"matching inventory sku len): {invSkuLen}")
            logger.debug(f"orderPartSkuColor): {len(orderPartSkuColor)}")
            #create the manufacturing list if it is not already created
            if (ManufacturingLists.objects.filter(order_id=order).exists()) == False:
                logger.debug("**Creating manufacturing list 2nd if block")
                manuList = ManufacturingLists.objects.create(status = 'Pending', order_id=order)
            else: #retrieve the manufacturing list if it already exists
                manuList = ManufacturingLists.objects.get(order_id=order)
            manuListItems= [] #create list of manufacturing list items
            #if there is no inventory picklist for the order, then create all the parts in the order as manufacturing list items
            logger.debug(f"Is there a picklist?: {InventoryPicklist.objects.filter(order_id=order).exists()}")
            if (InventoryPicklist.objects.filter(order_id=order).exists()) == False:
                logger.debug("there is no picklist")
                for s in orderPartSkuColor:
                    logger.debug(f"add manuList item {s}")
                    ##orderQty = OrderPart.objects.get(order_id=order, sku_color=s).__getattribute__("qty")
                    orderQty = OrderPart.objects.filter(order_id=order, sku_color=s).aggregate(total=Sum('qty'))['total']
                    manuListItems.append(ManufacturingListItem(sku_color=Part.objects.get(sku_color=s), manufacturing_list_id = manuList, amount=orderQty))
            else: #otherwise if there is an inventory picklist for the order, for the remaining order parts that did not get compared to the inventory items earlier (line 42 if block), make the manufacturing list item for them
                logger.debug("there was a picklist")
                inventoryPicklist = InventoryPicklist.objects.get(order_id=order)
                inventoryPicklistSkus = InventoryPicklistItem.objects.filter(picklist_id = inventoryPicklist).values_list('sku_color', flat=True)
                #***
                manuSkus = list(set(OrderPart.objects.filter(Q(order_id = order) & ~Q(sku_color__in = inventoryPicklistSkus)).values_list('sku_color', flat=True)))
                logger.debug(f"manuSkus: {manuSkus}")
                for s in manuSkus:
                    ##orderQty = OrderPart.objects.get(order_id=order, sku_color=Part.objects.get(sku_color=s)).__getattribute__("qty")
                    orderQty = OrderPart.objects.filter(order_id=order, sku_color=s).aggregate(total=Sum('qty'))['total']
                    logger.debug("add manuList item")
                    manuListItems.append(ManufacturingListItem(sku_color=Part.objects.get(sku_color=s), manufacturing_list_id=manuList, amount = orderQty))
            ManufacturingListItem.objects.bulk_create(manuListItems)
        #create empty inventory picklist for the order
        inventoryPicklist = InventoryPicklist.objects.get_or_create(status = False, order_id=order)

        #'''
        try:
            manuList = ManufacturingLists.objects.get(order_id = order)
        except ManufacturingLists.DoesNotExist:
            manuList = None
            logger.error("Manufacturing list for order %s does not exist (GenerateInventoryAndManufacturingListsView)", orderID)
            return Response({'error':'manufacturing list does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        logger.debug(f"manufacturing list object: {manuList}")
        if manuList != None:
            logger.debug("All Manufacturing List Items: %s", ', '.join([str(x) for x in ManufacturingListItem.objects.filter(manufacturing_list_id = manuList)]))
        #'''

        logger.info("Successfully generated the inventory picklist and manufacturing for order %s", orderID)
        return Response({'detail':'inventory picklist and manufacturing list generation successful'}, status=status.HTTP_200_OK)


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

            logger.info("Fetched all order data from database")
            return Response(inventory_data)
        except Exception as e:
            logger.error("Failed to query orders from database (OrdersView)")
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
            logger.info("Successfully started an order")
            return JsonResponse({
                'status': 'success',  # Overall success of the action
                'order_id': order.order_id,
                'order_status': order.status,  # Changed this from 'status' to 'order_status'
                'start_timestamp': order.start_timestamp.isoformat()  # ISO 8601 formatted timestamp
            })

        except Exception as e:
            # In case of any error, return error details
            logger.error("Failed to start an order (StartOrderView)")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        


class InventoryPicklistView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch started orders (status='In Progress') and their picklists
            started_orders = Orders.objects.filter(status='In Progress').values(
                'order_id', 'due_date'
            )

            # Build response data with additional fields `already_filled` and `assigned_to`
            response_data = [
                {
                    "order_id": order['order_id'],
                    "due_date": order['due_date'],
                    # Determine if the picklist is filled (all items are marked as `True`)
                    "already_filled": InventoryPicklistItem.objects.filter(
                        picklist_id__order_id=order['order_id'], status=False
                    ).exists() == False,
                    # Get the assigned employee from the picklist, if any
                    "assigned_to": InventoryPicklist.objects.filter(
                        order_id=order['order_id']
                    ).values_list('assigned_employee_id__username', flat=True).first()
                }
                for order in started_orders
            ]

            logger.info("Successfully fetched all started orders, their associated picklists, and their states")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Failed to fetched all started orders (InventoryPicklistView)")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class InventoryPicklistItemsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        try:
            # Fetch the order based on the provided order_id
            order = Orders.objects.get(order_id=order_id)

            # Fetch the inventory picklist associated with the order
            picklist = InventoryPicklist.objects.get(order_id=order)

            # Fetch picklist items for the given picklist
            picklist_items = InventoryPicklistItem.objects.filter(
                picklist_id=picklist.picklist_id
            ).values(
                'picklist_item_id',
                'location__location',
                'sku_color__sku_color',
                'amount',
                'status'
            )

            # Build response data
            response_data = [
                {
                    "picklist_item_id": item['picklist_item_id'],
                    "location": item['location__location'],
                    "sku_color": item['sku_color__sku_color'],
                    "quantity": item['amount'],
                    "status": item['status']
                }
                for item in picklist_items
            ]

            logger.info("Successfully retrieved all items from picklist %s and their states", picklist.picklist_id)
            return Response(response_data, status=status.HTTP_200_OK)

        except Orders.DoesNotExist:
            logger.error("Order could not be found (InventoryPicklistItemsView)")
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except InventoryPicklist.DoesNotExist:
            logger.error("Picklist could not be found for order %s (InventoryPicklistItemsView)", order_id)
            return Response(
                {"error": "No picklist found for the given order"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error("Failed to retrieve picklist items associated with order %s", order_id)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )