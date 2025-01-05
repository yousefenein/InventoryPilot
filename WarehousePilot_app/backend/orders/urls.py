from django.urls import path
from .views import GenerateInventoryAndManufacturingListsView

from . import views
from .views import OrdersView


urlpatterns = [
 Generate-inventory-and-manu-lists-for-an-order
    path('generateLists/', GenerateInventoryAndManufacturingListsView.as_view(), name="generateLists"),

    path("ordersview/", OrdersView.as_view(), name="ordersview"),
]