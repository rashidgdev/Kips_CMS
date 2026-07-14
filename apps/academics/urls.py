from django.urls import path

from . import views

app_name = 'academics'

urlpatterns = [
    path('programs/', views.ProgramListView.as_view(), name='programs'),
    path('programs/new/', views.ProgramCreateView.as_view(), name='program-new'),
    path('programs/<int:pk>/edit/', views.ProgramUpdateView.as_view(), name='program-edit'),
    path('programs/<int:pk>/delete/', views.ProgramDeleteView.as_view(), name='program-delete'),

    path('semesters/', views.SemesterListView.as_view(), name='semesters'),
    path('semesters/new/', views.SemesterCreateView.as_view(), name='semester-new'),
    path('semesters/<int:pk>/edit/', views.SemesterUpdateView.as_view(), name='semester-edit'),
    path('semesters/<int:pk>/delete/', views.SemesterDeleteView.as_view(), name='semester-delete'),

    path('courses/', views.CourseListView.as_view(), name='courses'),
    path('courses/new/', views.CourseCreateView.as_view(), name='course-new'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course-edit'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),

    path('offerings/', views.CourseOfferingListView.as_view(), name='offerings'),
    path('offerings/new/', views.CourseOfferingCreateView.as_view(), name='offering-new'),
    path('offerings/<int:pk>/edit/', views.CourseOfferingUpdateView.as_view(), name='offering-edit'),
    path('offerings/<int:pk>/delete/', views.CourseOfferingDeleteView.as_view(), name='offering-delete'),

    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollments'),
    path('enrollments/new/', views.EnrollmentCreateView.as_view(), name='enrollment-new'),
    path('enrollments/<int:pk>/edit/', views.EnrollmentUpdateView.as_view(), name='enrollment-edit'),
    path('enrollments/<int:pk>/delete/', views.EnrollmentDeleteView.as_view(), name='enrollment-delete'),
]
