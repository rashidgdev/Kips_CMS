from django.urls import path

from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.semester_grid, name='grid'),
    path('semester/<int:semester_id>/', views.semester_grid, name='grid-for-semester'),
    path('semester/<int:semester_id>/schedule/', views.schedule_entry, name='schedule'),
    path('entries/<int:entry_id>/remove/', views.unschedule_entry, name='unschedule'),
    path('mine/', views.teacher_timetable, name='teacher-mine'),
    path('my/', views.student_timetable, name='student-mine'),

    path('rooms/', views.RoomListView.as_view(), name='rooms'),
    path('rooms/new/', views.RoomCreateView.as_view(), name='room-new'),
    path('rooms/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room-edit'),
    path('rooms/<int:pk>/delete/', views.RoomDeleteView.as_view(), name='room-delete'),

    path('timeslots/', views.TimeSlotListView.as_view(), name='timeslots'),
    path('timeslots/new/', views.TimeSlotCreateView.as_view(), name='timeslot-new'),
    path('timeslots/<int:pk>/edit/', views.TimeSlotUpdateView.as_view(), name='timeslot-edit'),
    path('timeslots/<int:pk>/delete/', views.TimeSlotDeleteView.as_view(), name='timeslot-delete'),
]
