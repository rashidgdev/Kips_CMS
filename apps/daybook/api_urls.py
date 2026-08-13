from django.urls import path

from . import api_views

app_name = 'daybook_api'

urlpatterns = [
    path('mine/', api_views.day_book_list_api, name='mine'),
    path('verify-queue/', api_views.verify_queue_api, name='verify-queue'),
    path('verify/<int:entry_id>/', api_views.verify_entry_api, name='verify'),
    path('workload/', api_views.workload_report_api, name='workload-report'),
    path('workload/generate/', api_views.workload_snapshot_generate_api, name='workload-generate'),
]
