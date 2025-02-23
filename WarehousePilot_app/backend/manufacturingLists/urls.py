from django.urls import path


from .views import ManufacturingListView, ManufacturingListItemsView, ManufacturingTaskView


urlpatterns = [
    path('manufacturing_list/', ManufacturingListView.as_view(), name="manufacturing_list"),
    path('manufacturing_list_item/<int:order_id>/', ManufacturingListItemsView.as_view(), name="manufacturing_list_item"),
    # example query manufacturing_list/manufacturing_tasks/?department=nesting
    path('manufacturing_tasks/', ManufacturingTaskView.as_view(), name="manufacturing_tasks")
    
]
