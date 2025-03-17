
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q, Min
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
import logging
from inventory.models import InventoryPicklist, InventoryPicklistItem

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
from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from orders.models import Orders, OrderPart
from manufacturingLists.models import ManufacturingTask
from inventory.models import Part
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import logging
import traceback

logger = logging.getLogger(__name__)

def order_fulfillment_rate(request):
    """
    API endpoint to get order fulfillment statistics filtered by date range.
    Supports filtering by 'day', 'week', or 'month'.
    Allows users to specify a custom date for filtering.
    """
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        logger.debug("Starting order_fulfillment_rate function")

        # Get filter type (default: monthly)
        filter_type = request.GET.get('filter', 'month').lower()
        reference_date = request.GET.get('date', None)

        if reference_date:
            try:
                reference_date = datetime.strptime(reference_date, "%Y-%m-%d")
            except ValueError:
                return JsonResponse({"error": "Invalid date format, expected YYYY-MM-DD"}, status=400)
        else:
            reference_date = datetime.now()

        # Determine truncation function and period range
        if filter_type == 'day':
            trunc_function = TruncDay('start_timestamp')
            period_start = reference_date.replace(hour=0, minute=0, second=0)
            period_end = reference_date.replace(hour=23, minute=59, second=59)

        elif filter_type == 'week':
            trunc_function = TruncWeek('start_timestamp')
            period_start = reference_date - timedelta(days=reference_date.weekday())  # Start of the week (Monday)
            period_end = period_start + timedelta(days=6, hours=23, minutes=59, seconds=59)  # End of the week (Sunday)

        else:  # Default to 'month'
            trunc_function = TruncMonth('start_timestamp')
            period_start = reference_date.replace(day=1, hour=0, minute=0, second=0)
            period_end = period_start + relativedelta(months=1, seconds=-1)  # Last second of the month

        logger.debug(f"Filtering orders from {period_start} to {period_end}")

        # Get orders started in the selected period
        orders_qs = (
            Orders.objects
            .filter(start_timestamp__gte=period_start, start_timestamp__lte=period_end)
            .annotate(period=trunc_function)
            .values('period')
            .annotate(total_orders_started=Count('order_id'))  # Renamed from total_orders
            .order_by('period')
        )

        logger.debug(f"Orders query returned {len(orders_qs)} periods")

        data = []
        for entry in orders_qs:
            period_date = entry['period']
            if not period_date:
                continue  # Skip invalid periods

            # Orders within this period
            period_orders = Orders.objects.filter(start_timestamp__gte=period_date, start_timestamp__lt=period_end)
            order_ids = list(period_orders.values_list('order_id', flat=True))
            
            # Get orders_started without exclusions
            orders_started = period_orders.count()
            
            # Get ALL orders in the system for total count (regardless of period)
            total_orders_count = Orders.objects.count()

            if not order_ids:
                data.append({
                    "period": period_date.strftime("%Y-%m-%d"),
                    "total_orders_started": entry['total_orders_started'],  # Renamed from total_orders
                    "total_orders_count": total_orders_count,
                    "orders_started": orders_started,  # Now without exclusions
                    "partially_fulfilled": 0,
                    "fully_fulfilled": 0,
                })
                continue

            # Get parts associated with these orders through OrderPart
            parts = Part.objects.filter(orderpart__order_id__in=order_ids)
            part_skus = list(parts.values_list('sku_color', flat=True))

            if not part_skus:
                data.append({
                    "period": period_date.strftime("%Y-%m-%d"),
                    "total_orders_started": entry['total_orders_started'],  # Renamed from total_orders
                    "total_orders_count": total_orders_count,
                    "orders_started": orders_started,  # Now without exclusions
                    "partially_fulfilled": 0,
                    "fully_fulfilled": 0,
                })
                continue

            # Count partially fulfilled orders (Orders that have at least one ManufacturingTask in progress)
            partially_fulfilled_orders = OrderPart.objects.filter(
                order_id__in=order_ids,
                sku_color__manufacturingtask__status__in=["nesting", "bending", "cutting", "welding", "painting"]
            ).values('order_id').distinct().count()

            # Count fully fulfilled orders (Orders where all ManufacturingTasks are completed)
            fully_fulfilled_orders = OrderPart.objects.filter(
                order_id__in=order_ids,
                sku_color__manufacturingtask__status="completed"
            ).values('order_id').distinct().count()

            data.append({
                "period": period_date.strftime("%Y-%m-%d"),
                "total_orders_started": entry['total_orders_started'],  # Renamed from total_orders
                "total_orders_count": total_orders_count,
                "orders_started": orders_started,  # Now without exclusions
                "partially_fulfilled": partially_fulfilled_orders,
                "fully_fulfilled": fully_fulfilled_orders,
            })

            logger.debug(f"Added data entry for {period_date}")

        logger.debug(f"Final data count: {len(data)}")
        return JsonResponse(data, safe=False)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({"error": str(e), "traceback": traceback.format_exc()}, status=500)
    
class ActiveOrdersView(APIView):
    def get(self, request):
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            # Debug: Log picklists and Orders data
            total_picklists = InventoryPicklist.objects.count()
            picklist_statuses = InventoryPicklist.objects.values('status').distinct()
            orders_statuses = InventoryPicklist.objects.values('order_id__status').distinct()
            logger.info("Total picklists in database: %s", total_picklists)
            logger.info("Distinct picklist status values: %s", [s['status'] for s in picklist_statuses])
            logger.info("Distinct order status values: %s", [s['order_id__status'] for s in orders_statuses])

            # Active Orders: Picklists where status=False and Orders status="In Progress"
            active_orders = (
                InventoryPicklist.objects
                .filter(
                    status=False,
                    order_id__status="In Progress",
                    order_id__start_timestamp__date__gte=start_date,
                    order_id__start_timestamp__date__lte=end_date
                )
                .annotate(date=TruncDate('order_id__start_timestamp'))
                .values('date')
                .annotate(active_orders=Count('picklist_id', distinct=True))
                .order_by('date')
            )

            date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
            active_orders_dict = {entry['date']: entry['active_orders'] for entry in active_orders}
            response_data = [
                {"date": day.strftime('%Y-%m-%d'), "active_orders": active_orders_dict.get(day, 0)}
                for day in date_range
            ]
            logger.info("Active orders data: %s", response_data)
            return Response(response_data, status=200)
        except Exception as e:
            logger.error(f"Failed to fetch active orders data: {str(e)}")
            return Response({"error": str(e)}, status=500)

class CompletedOrdersView(APIView):
    def get(self, request):
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            # Completed Orders: Picklists where status=True and Orders status="Completed"
            completed_orders = (
                InventoryPicklist.objects
                .filter(
                    status=True,
                    order_id__status="Completed",
                    picklist_complete_timestamp__date__gte=start_date,
                    picklist_complete_timestamp__date__lte=end_date
                )
                .annotate(date=TruncDate('picklist_complete_timestamp'))
                .values('date')
                .annotate(completed_orders=Count('picklist_id', distinct=True))
                .order_by('date')
            )

            date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
            completed_orders_dict = {entry['date']: entry['completed_orders'] for entry in completed_orders}
            response_data = [
                {"date": day.strftime('%Y-%m-%d'), "completed_orders": completed_orders_dict.get(day, 0)}
                for day in date_range
            ]
            logger.info("Completed orders data: %s", response_data)
            return Response(response_data, status=200)
        except Exception as e:
            logger.error(f"Failed to fetch completed orders data: {str(e)}")
            return Response({"error": str(e)}, status=500)