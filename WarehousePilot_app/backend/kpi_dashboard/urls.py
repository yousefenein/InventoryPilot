from django.urls import path
from . import views

urlpatterns = [
    path('order-picking-accuracy/', views.order_picking_accuracy, name='order_picking_accuracy'),
]