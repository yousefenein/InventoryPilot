from django.urls import path


from .views import ManufacturingListView


urlpatterns = [
    path('manufacturing_list/', ManufacturingListView.as_view(), name="manufacturing_list"),
    
]
