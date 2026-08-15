from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html', authentication_form=StyledAuthenticationForm
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password/change/', views.ChangePasswordView.as_view(), name='password-change'),
    path('profile/', views.profile, name='profile'),
    path('departments/', views.DepartmentListView.as_view(), name='departments'),
    path('departments/new/', views.DepartmentFormView.as_view(), name='department-new'),
    path('departments/<int:pk>/edit/', views.DepartmentFormView.as_view(), name='department-edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department-delete'),
    path('people/', views.people_directory, name='people'),
    path('people/<int:user_id>/', views.person_profile, name='person-profile'),
    path('people/<int:user_id>/toggle-active/', views.toggle_active, name='toggle-active'),
    path('people/students/new/', views.student_create, name='student-new'),
    path('people/students/<int:profile_id>/edit/', views.student_edit, name='student-edit'),
    path('people/teachers/new/', views.teacher_create, name='teacher-new'),
    path('people/teachers/<int:profile_id>/edit/', views.teacher_edit, name='teacher-edit'),
    path('people/staff/new/', views.staff_create, name='staff-new'),
    path('people/staff/<int:profile_id>/edit/', views.staff_edit, name='staff-edit'),

    path('people/students/import/', views.student_import, name='student-import'),
    path('people/students/import/results/', views.student_import_results, name='student-import-results'),
    path('people/students/import/results/csv/', views.student_import_csv, name='student-import-csv'),
    path('people/students/import/template/', views.student_import_template, name='student-import-template'),

    path('people/teachers/import/', views.teacher_import, name='teacher-import'),
    path('people/teachers/import/results/', views.teacher_import_results, name='teacher-import-results'),
    path('people/teachers/import/results/csv/', views.teacher_import_csv, name='teacher-import-csv'),
    path('people/teachers/import/template/', views.teacher_import_template, name='teacher-import-template'),
]
