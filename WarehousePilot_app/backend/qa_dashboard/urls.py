from django.urls import path
from .views import QADashboardView, QAManufacturingTasksView, UpdateQATaskView, ReportQAErrorView, UpdateQAStatusView

urlpatterns = [
    path('', QADashboardView.as_view(), name='qa_dashboard'),
    path('qa_tasks/', QAManufacturingTasksView.as_view(), name='qa_tasks'),
    path('qa_tasks/update/', UpdateQATaskView.as_view(), name='update_qa_task'),
    path('qa_tasks/report_error/', ReportQAErrorView.as_view(), name='report_qa_error'),
    path('qa_tasks/update_status/', UpdateQAStatusView.as_view(), name='update_qa_status'),
]
