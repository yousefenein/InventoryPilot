from django.urls import path

from . import views
from .views import InventoryPickingLogging

urlpatterns = [
    path("", InventoryPickingLogging.as_view(), name="inventory_picking_logging"),
]