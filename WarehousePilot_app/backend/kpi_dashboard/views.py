from django.http import JsonResponse
from django.db.models import Count
from inventory.models import InventoryPicklistItem

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