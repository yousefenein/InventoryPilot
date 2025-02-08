from django.urls import path
from .views import order_picking_accuracy

urlpatterns = [
    path('api/order-picking-accuracy/', order_picking_accuracy, name='order_picking_accuracy'),
]