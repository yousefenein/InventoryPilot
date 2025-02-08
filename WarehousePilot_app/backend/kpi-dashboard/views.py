from django.http import JsonResponse
from django.db.models import Count
from .models import InventoryPicklistItem 

def order_picking_accuracy(request):
    # Query the database
    total_picks = InventoryPicklistItem.objects.count()
    accurate_picks = InventoryPicklistItem.objects.filter(status=True).count()
    inaccurate_picks = total_picks - accurate_picks

    # Prepare the data
    data = {
        "accurate_picks": accurate_picks,
        "inaccurate_picks": inaccurate_picks,
    }

    return JsonResponse(data)