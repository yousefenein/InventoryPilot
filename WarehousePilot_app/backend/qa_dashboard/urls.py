from django.urls import path
from .views import QADashboardView, QAManufacturingTasksView, MarkQATaskCompleteView, ReportQAErrorView

urlpatterns = [
    path('', QADashboardView.as_view(), name='qa_dashboard'),
    path('qa_tasks/', QAManufacturingTasksView.as_view(), name='qa_tasks'),
    path('qa_tasks/complete/', MarkQATaskCompleteView.as_view(), name='mark_qa_complete'),
    path('qa_tasks/error/', ReportQAErrorView.as_view(), name='report_qa_error'),
]

