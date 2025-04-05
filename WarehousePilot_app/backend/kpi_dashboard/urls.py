from django.urls import path
from . import views
from .views import daily_picks_data, daily_picks_details, order_fulfillment_rate, ThroughputView

urlpatterns = [
    path('order-picking-accuracy/', views.order_picking_accuracy, name='order_picking_accuracy'),
    path('order-picking-daily-stats/', daily_picks_data, name='daily_picks_data'),
    path('order-picking-daily-details/', daily_picks_details, name='daily_picks_details'),
    path('order-fulfillment-rate/', order_fulfillment_rate, name='order_fulfillment_rate'),  
    path('active-orders/', views.ActiveOrdersView.as_view(), name='active_orders'),  
    path('completed-orders/', views.CompletedOrdersView.as_view(), name='completed_orders'), 
    path('active-orders-details/', views.ActiveOrdersDetailsView.as_view(), name='active_orders_details'),
    path('throughput-threshold/', views.ThroughputView.as_view(), name='throughput_threshold'), 

]