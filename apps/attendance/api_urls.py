from django.urls import path

from . import api_views

app_name = 'attendance_api'

urlpatterns = [
    path('offerings/', api_views.offering_list_api, name='offerings'),
    path('offerings/<int:offering_id>/sessions/', api_views.session_list_api, name='sessions'),
    path('sessions/<int:session_id>/mark/', api_views.mark_attendance_api, name='mark'),
    path('my/', api_views.student_overview_api, name='student-overview'),
    path('my/<int:offering_id>/', api_views.student_course_detail_api, name='student-detail'),
]
