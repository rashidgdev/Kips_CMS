from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api_views

app_name = 'accounts_api'

router = SimpleRouter(trailing_slash=True)
router.register('departments', api_views.DepartmentViewSet, basename='department')

urlpatterns = [
    # JWT auth for the mobile app - additive, the web app keeps using its
    # session login untouched. POST {"username", "password"} -> {"access", "refresh"}.
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('me/', api_views.me, name='me'),
    path('me/photo/', api_views.update_my_photo, name='me-photo'),
    path('change-password/', api_views.change_password, name='change-password'),

    path('people/', api_views.PeopleListAPIView.as_view(), name='people'),
    path('people/<int:user_id>/toggle-active/', api_views.toggle_active, name='toggle-active'),

    path('students/', api_views.student_create, name='student-create'),
    path('students/<int:profile_id>/', api_views.student_update, name='student-update'),
    path('teachers/', api_views.teacher_create, name='teacher-create'),
    path('teachers/<int:profile_id>/', api_views.teacher_update, name='teacher-update'),
    path('staff/', api_views.staff_create, name='staff-create'),
    path('staff/<int:profile_id>/', api_views.staff_update, name='staff-update'),
] + router.urls
