from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('offerings/', views.offering_list, name='offerings'),
    path('offerings/<int:offering_id>/sessions/', views.session_list, name='sessions'),
    path('offerings/<int:offering_id>/sessions/new/', views.session_create, name='session-new'),
    path('sessions/<int:session_id>/mark/', views.mark_attendance, name='mark'),
    path('my/', views.student_overview, name='student-overview'),
    path('my/<int:offering_id>/', views.student_course_detail, name='student-detail'),
]
