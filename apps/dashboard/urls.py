from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_redirect, name='redirect'),
    path('student/', views.student_dashboard, name='student'),
    path('teacher/', views.teacher_dashboard, name='teacher'),
    path('hod/', views.hod_dashboard, name='hod'),
    path('coordinator/', views.coordinator_dashboard, name='coordinator'),
    path('accountant/', views.accountant_dashboard, name='accountant'),
    path('admin-panel/', views.admin_dashboard, name='admin'),
    path('administration/', views.admin_portal, name='admin-portal'),
]
