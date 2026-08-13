from django.urls import path
from rest_framework.routers import SimpleRouter

from . import api_views

app_name = 'assessments_api'

router = SimpleRouter(trailing_slash=True)
router.register('categories', api_views.AssessmentCategoryViewSet, basename='category')

urlpatterns = [
    path('category-options/', api_views.category_options_api, name='category-options'),
    path('offerings/', api_views.offering_list_api, name='offerings'),
    path('offerings/<int:offering_id>/assessments/', api_views.assessment_list_api, name='assessments'),
    path('assessments/<int:assessment_id>/marks/', api_views.enter_marks_api, name='marks'),
    path('my/', api_views.student_overview_api, name='student-overview'),
    path('my/<int:offering_id>/', api_views.student_course_detail_api, name='student-detail'),
] + router.urls
