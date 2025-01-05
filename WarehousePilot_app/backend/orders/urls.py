from django.urls import path
from .views import GenerateInventoryAndManufacturingListsView

from . import views
from .views import OrdersView


urlpatterns = [
    path('generateLists/', GenerateInventoryAndManufacturingListsView.as_view(), name="generateLists"),
    path("ordersview/", OrdersView.as_view(), name="ordersview"),
]
