from datetime import timedelta
from django.http import JsonResponse
from django.db.models import Count
from inventory.models import InventoryPicklistItem
from django.db.models.functions import TruncDay


def order_picking_accuracy(request):
    if request.method == 'GET':
        accurate_picks = InventoryPicklistItem.objects.filter(status=True).count()
        total_picks = InventoryPicklistItem.objects.count()
        inaccurate_picks = total_picks - accurate_picks

        # Calculate accuracy percentage
        accuracy_percentage = (accurate_picks / total_picks * 100) if total_picks > 0 else 0

        # Define the target accuracy (e.g., 99%)
        target_accuracy = 99

        data = {
            'accurate_picks': accurate_picks,
            'inaccurate_picks': inaccurate_picks,
            'accuracy_percentage': round(accuracy_percentage, 2),  # Round to 2 decimal places
            'target_accuracy': target_accuracy,
        }

        return JsonResponse(data)
    
    
def daily_picks_data(request):
    """
    Returns total picked items per day, based on InventoryPicklistItem.picked_at.
    Only counts items where status=True (meaning it's actually picked).
    """
    if request.method == 'GET':
        picks_by_day_qs = (
            InventoryPicklistItem.objects
            .filter(status=True)
            .annotate(day=TruncDay('picked_at'))   # group by date portion
            .values('day')
            .annotate(picks=Count('picklist_item_id'))
            .order_by('day')
        )

        
        data = []
        for entry in picks_by_day_qs:
            if entry['day']:
                data.append({
                    "day": entry['day'].strftime("%Y-%m-%d"),
                    "picks": entry['picks'],
                })

        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)    
    
    
    
def daily_picks_details(request):
    """
    Returns a breakdown of picked items, grouped by day and order_id.
    
    """
    if request.method == 'GET':
        # Only count items where status=True (actually picked)
        picks_by_day_and_order = (
            InventoryPicklistItem.objects
            .filter(status=True)
            .annotate(day=TruncDay('picked_at'))  
            .values('day', 'picklist_id__order_id')  
            .annotate(picks=Count('picklist_item_id'))
            .order_by('day', 'picklist_id__order_id')
        )

        data = []
        for row in picks_by_day_and_order:
            day_value = row['day']
            order_id = row['picklist_id__order_id']
            picks_count = row['picks']

            data.append({
                "day": day_value.strftime("%Y-%m-%d") if day_value else None,
                "order_id": str(order_id),
                "picks": picks_count
            })

        return JsonResponse(data, safe=False)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)    
    
    
    


from django.http import JsonResponse
from django.db.models import Count, Q, Exists, OuterRef
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from orders.models import Orders
from manufacturingLists.models import ManufacturingTask
from inventory.models import Part
import logging
from datetime import timedelta, datetime
import traceback

logger = logging.getLogger(__name__)

def order_fulfillment_rate(request):
    """
    API endpoint to get order fulfillment statistics filtered by date range.
    Supports filtering by 'day', 'week', or 'month'.
    """
    if request.method == 'GET':
        try:
            logger.debug("Starting order_fulfillment_rate function")
            
            # Get filter type (default: monthly)
            filter_type = request.GET.get('filter', 'month')
            logger.debug(f"Filter type: {filter_type}")
            
            # Determine the appropriate time truncation function and date range
            if filter_type == 'day':
                trunc_function = TruncDay('start_timestamp')
                # Optionally, limit to recent days to avoid too many data points
                date_limit = datetime.now() - timedelta(days=30)  # Last 30 days
            elif filter_type == 'week':
                trunc_function = TruncWeek('start_timestamp')
                # Limit to recent weeks
                date_limit = datetime.now() - timedelta(weeks=12)  # Last 12 weeks
            else:  # Default to 'month'
                trunc_function = TruncMonth('start_timestamp')
                date_limit = datetime.now() - timedelta(days=365)  # Last 12 months
            
            # Query orders and classify them based on fulfillment status
            try:
                orders_qs = (
                    Orders.objects
                    .filter(start_timestamp__gte=date_limit)  # Add date limit
                    .annotate(period=trunc_function)
                    .values('period')
                    .annotate(
                        total_orders=Count('order_id'),
                    )
                    .order_by('period')
                )
                logger.debug(f"Orders query successful, count: {len(orders_qs)}")
            except Exception as e:
                logger.error(f"Error in orders query: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({"error": f"Orders query error: {str(e)}"}, status=500)
            
            # Process each period to calculate fulfillment statuses
            data = []
            
            for entry in orders_qs:
                logger.debug(f"Processing entry: {entry}")
                
                if entry['period']:
                    period_start = entry['period']
                    logger.debug(f"Period start: {period_start}")
                    
                    try:
                        # Calculate the end date for this period based on the filter type
                        if filter_type == 'day':
                            period_end = period_start + timedelta(days=1)
                        elif filter_type == 'week':
                            period_end = period_start + timedelta(days=7)
                        else:  # month
                            # For month, we need to go to the next month's same day
                            # This is more accurate than just adding 30 days
                            if period_start.month == 12:
                                period_end = period_start.replace(year=period_start.year + 1, month=1)
                            else:
                                period_end = period_start.replace(month=period_start.month + 1)
                        
                        logger.debug(f"Period end: {period_end}")
                        
                        # For the given period, find all orders
                        period_orders = Orders.objects.filter(
                            start_timestamp__gte=period_start,
                            start_timestamp__lt=period_end
                        )
                        logger.debug(f"Period orders count: {period_orders.count()}")
                        
                        # Get order IDs for this period
                        order_ids = list(period_orders.values_list('order_id', flat=True))
                        logger.debug(f"Order IDs count: {len(order_ids)}")
                        
                        # Count various fulfillment states
                        orders_started = period_orders.exclude(status__in=["Not Started", None]).count()
                        logger.debug(f"Orders started: {orders_started}")
                        
                        # Handle empty order_ids list
                        if not order_ids:
                            data.append({
                                "period": period_start.strftime("%Y-%m-%d"),
                                "total_orders": entry['total_orders'],
                                "orders_started": orders_started,
                                "partially_fulfilled": 0,
                                "fully_fulfilled": 0,
                            })
                            continue
                        
                        try:
                            # Parts associated with these orders
                            parts = Part.objects.filter(order_id__in=order_ids)
                            part_count = parts.count()
                            logger.debug(f"Parts count: {part_count}")
                            
                            if part_count == 0:
                                # No parts for these orders
                                data.append({
                                    "period": period_start.strftime("%Y-%m-%d"),
                                    "total_orders": entry['total_orders'],
                                    "orders_started": orders_started,
                                    "partially_fulfilled": 0,
                                    "fully_fulfilled": 0,
                                })
                                continue
                            
                            part_skus = list(parts.values_list('sku_color', flat=True))
                            logger.debug(f"Part SKUs count: {len(part_skus)}")
                            
                        except Exception as e:
                            logger.error(f"Error in parts query: {str(e)}")
                            logger.error(traceback.format_exc())
                            part_skus = []
                        
                        # Handle empty part_skus list
                        if not part_skus:
                            data.append({
                                "period": period_start.strftime("%Y-%m-%d"),
                                "total_orders": entry['total_orders'],
                                "orders_started": orders_started,
                                "partially_fulfilled": 0,
                                "fully_fulfilled": 0,
                            })
                            continue
                        
                        try:
                            # Count partially fulfilled orders (at least one task in progress)
                            tasks_in_progress = ManufacturingTask.objects.filter(
                                sku_color__in=part_skus,
                                status__in=["nesting", "bending", "cutting", "welding", "painting"]
                            ).values('sku_color').distinct()
                            
                            partially_fulfilled = len(tasks_in_progress)
                            logger.debug(f"Partially fulfilled: {partially_fulfilled}")
                            
                        except Exception as e:
                            logger.error(f"Error in partially fulfilled query: {str(e)}")
                            logger.error(traceback.format_exc())
                            partially_fulfilled = 0
                        
                        try:
                            # Count fully fulfilled orders (all tasks completed)
                            completed_tasks = ManufacturingTask.objects.filter(
                                sku_color__in=part_skus,
                                status="completed"
                            ).values('sku_color').distinct()
                            
                            fully_fulfilled = len(completed_tasks)
                            logger.debug(f"Fully fulfilled: {fully_fulfilled}")
                            
                        except Exception as e:
                            logger.error(f"Error in fully fulfilled query: {str(e)}")
                            logger.error(traceback.format_exc())
                            fully_fulfilled = 0
                        
                        data.append({
                            "period": period_start.strftime("%Y-%m-%d"),
                            "total_orders": entry['total_orders'],
                            "orders_started": orders_started,
                            "partially_fulfilled": partially_fulfilled,
                            "fully_fulfilled": fully_fulfilled,
                        })
                        logger.debug(f"Added data entry for period {period_start}")
                        
                    except Exception as e:
                        logger.error(f"Error processing period {period_start}: {str(e)}")
                        logger.error(traceback.format_exc())
            
            logger.debug(f"Final data count: {len(data)}")
            return JsonResponse(data, safe=False)
            
        except Exception as e:
            logger.error(f"Unexpected error in order_fulfillment_rate: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({
                "error": str(e), 
                "traceback": traceback.format_exc()
            }, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)