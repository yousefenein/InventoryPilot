from django.urls import path
from .views import GenerateInventoryAndManufacturingListsView

from . import views
from .views import OrdersView, StartOrderView


urlpatterns = [
    path('generateLists/', GenerateInventoryAndManufacturingListsView.as_view(), name="generateLists"),
    path("ordersview/", OrdersView.as_view(), name="ordersview"),
    path('start_order/<int:order_id>/', StartOrderView.as_view(), name='start_order'),
]
