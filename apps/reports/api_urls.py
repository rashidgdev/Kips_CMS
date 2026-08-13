from django.urls import path

from . import api_views

app_name = 'reports_api'

urlpatterns = [
    path('attendance/', api_views.attendance_report_api, name='attendance'),
    path('academic/', api_views.academic_report_api, name='academic'),
    path('merit-list/', api_views.merit_list_api, name='merit-list'),
    path('progress-students/', api_views.ProgressStudentsAPIView.as_view(), name='progress-students'),
    path('progress/<int:student_id>/', api_views.progress_report_api, name='progress'),
]
