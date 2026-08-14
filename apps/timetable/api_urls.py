from django.urls import path
from rest_framework.routers import SimpleRouter

from . import api_views

app_name = 'timetable_api'

router = SimpleRouter(trailing_slash=True)
router.register('rooms', api_views.RoomViewSet, basename='room')
router.register('timeslots', api_views.TimeSlotViewSet, basename='timeslot')

urlpatterns = [
    path('semesters/', api_views.semesters_list_api, name='semesters'),
    path('grid/', api_views.semester_grid_api, name='grid'),
    path('grid/<int:semester_id>/', api_views.semester_grid_api, name='grid-for-semester'),
    path('grid/<int:semester_id>/schedule/', api_views.schedule_entry_api, name='schedule'),
    path('grid/<int:semester_id>/auto-schedule/', api_views.auto_schedule_semester_api, name='auto-schedule'),
    path('entries/<int:entry_id>/', api_views.unschedule_entry_api, name='unschedule'),
    path('timeslots/generate/', api_views.timeslot_generate_api, name='timeslot-generate'),
    path('mine/teacher/', api_views.teacher_timetable_api, name='teacher-mine'),
    path('mine/student/', api_views.student_timetable_api, name='student-mine'),
] + router.urls
