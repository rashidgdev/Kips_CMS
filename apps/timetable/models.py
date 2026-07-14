from django.conf import settings
from django.db import models

from apps.academics.models import CourseOffering
from apps.common.models import TimeStampedModel


class TimeSlot(TimeStampedModel):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'

    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('day_of_week', 'start_time', 'end_time')

    def __str__(self):
        name = self.label or f'{self.start_time:%H:%M}-{self.end_time:%H:%M}'
        return f'{self.get_day_of_week_display()} {name}'


class Room(TimeStampedModel):
    class RoomType(models.TextChoices):
        CLASSROOM = 'classroom', 'Classroom'
        LAB = 'lab', 'Lab'

    name = models.CharField(max_length=50, unique=True)
    building = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveSmallIntegerField(default=40)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.CLASSROOM)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TimetableEntry(TimeStampedModel):
    course_offering = models.ForeignKey(
        CourseOffering, on_delete=models.CASCADE, related_name='timetable_entries'
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='timetable_entries')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name='timetable_entries')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )

    class Meta:
        ordering = ['time_slot']
        # Hard DB-level guarantee: a room can't host two classes in the same weekly slot.
        unique_together = ('room', 'time_slot')

    def __str__(self):
        return f'{self.course_offering} - {self.time_slot} - {self.room}'
