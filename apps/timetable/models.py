from django.conf import settings
from django.db import models

from apps.academics.models import CourseOffering
from apps.common.models import TimeStampedModel


def _fmt12(value):
    """Render a time value in 12-hour clock form, e.g. '8:30 AM'."""
    return value.strftime('%I:%M %p').lstrip('0')


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
        name = self.label or f'{_fmt12(self.start_time)}-{_fmt12(self.end_time)}'
        return f'{self.get_day_of_week_display()} {name}'

    @property
    def start_time_display(self):
        return _fmt12(self.start_time)

    @property
    def end_time_display(self):
        return _fmt12(self.end_time)


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
    joint_offerings = models.ManyToManyField(
        CourseOffering, blank=True, related_name='joint_timetable_entries',
        help_text='Other course offerings that also attend this same physical class '
                   '(e.g. two programs sharing one lecture) - not a separate booking.',
    )

    class Meta:
        ordering = ['time_slot']
        # Hard DB-level guarantee: a room can't host two classes in the same weekly slot.
        # A joint session isn't a second booking - it's a second offering attached to
        # this same row via joint_offerings, so this constraint still holds correctly.
        unique_together = ('room', 'time_slot')

    def __str__(self):
        return f'{self.course_offering} - {self.time_slot} - {self.room}'

    @property
    def all_offerings(self):
        """The primary offering plus every joint one - what every grid/PDF/API
        renderer should iterate over instead of just `course_offering`."""
        return [self.course_offering, *self.joint_offerings.all()]
