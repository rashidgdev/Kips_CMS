from django.urls import path

from . import views

app_name = 'daybook'

urlpatterns = [
    path('', views.day_book_list, name='mine'),
    path('verify/', views.verify_queue, name='verify-queue'),
    path('verify/<int:entry_id>/', views.verify_entry, name='verify'),
    path('workload/', views.workload_report, name='workload-report'),
    path('workload/export/', views.workload_report_csv, name='workload-export'),
    path('workload/export/excel/', views.workload_report_excel, name='workload-export-excel'),
    path('workload/export/pdf/', views.workload_report_pdf, name='workload-export-pdf'),
]
