from django.urls import path
from rest_framework.routers import SimpleRouter

from . import api_views

app_name = 'academics_api'

router = SimpleRouter(trailing_slash=True)
router.register('programs', api_views.ProgramViewSet, basename='program')
router.register('semesters', api_views.SemesterViewSet, basename='semester')
router.register('courses', api_views.CourseViewSet, basename='course')
router.register('offerings', api_views.CourseOfferingViewSet, basename='offering')
router.register('enrollments', api_views.EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('enroll-by-offering/', api_views.enroll_by_offering_api, name='enroll-by-offering'),
    path('enroll-by-student/', api_views.enroll_by_student_api, name='enroll-by-student'),
] + router.urls
