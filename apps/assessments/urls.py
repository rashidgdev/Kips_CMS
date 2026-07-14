from django.urls import path

from . import views

app_name = 'assessments'

urlpatterns = [
    path('offerings/', views.offering_list, name='offerings'),
    path('offerings/<int:offering_id>/', views.assessment_list, name='assessments'),
    path('offerings/<int:offering_id>/new/', views.assessment_create, name='assessment-new'),
    path('assessments/<int:assessment_id>/marks/', views.enter_marks, name='marks'),
    path('my/', views.student_overview, name='student-overview'),
    path('my/<int:offering_id>/', views.student_course_detail, name='student-detail'),

    path('categories/', views.AssessmentCategoryListView.as_view(), name='categories'),
    path('categories/new/', views.AssessmentCategoryCreateView.as_view(), name='category-new'),
    path('categories/<int:pk>/edit/', views.AssessmentCategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.AssessmentCategoryDeleteView.as_view(), name='category-delete'),
]
