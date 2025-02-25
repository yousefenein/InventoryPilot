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