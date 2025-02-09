from django.urls import path
from .views import get_label_data

urlpatterns = [
    path('<int:picklist_item_id>/', get_label_data, name='get_label_data'),
]