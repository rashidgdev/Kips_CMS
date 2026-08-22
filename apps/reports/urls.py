from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='home'),
    path('attendance/', views.attendance_report, name='attendance'),
    path('attendance/export/excel/', views.attendance_report_excel, name='attendance-export-excel'),
    path('attendance/export/pdf/', views.attendance_report_pdf, name='attendance-export-pdf'),
    path('academic/', views.academic_report, name='academic'),
    path('academic/export/excel/', views.academic_report_excel, name='academic-export-excel'),
    path('academic/export/pdf/', views.academic_report_pdf, name='academic-export-pdf'),
    path('merit-list/', views.merit_list, name='merit-list'),
    path('merit-list/export/excel/', views.merit_list_excel, name='merit-export-excel'),
    path('merit-list/export/pdf/', views.merit_list_pdf, name='merit-export-pdf'),
    path('teacher-assignments/', views.teacher_assignments, name='teacher-assignments'),

    path('progress/students/', views.progress_students, name='progress-students'),
    path('progress/my/', views.my_progress_report, name='my-progress'),
    path('progress/<int:student_id>/', views.progress_report, name='progress'),
    path('progress/<int:student_id>/pdf/', views.progress_report_pdf, name='progress-pdf'),
]
