from django.urls import path


from .views import ManufacturingListView, ManufacturingListItemsView


urlpatterns = [
    path('manufacturing_list/', ManufacturingListView.as_view(), name="manufacturing_list"),
    path('manufacturing_list_item/<int:order_id>/', ManufacturingListItemsView.as_view(), name="manufacturing_list_item")
    
]
