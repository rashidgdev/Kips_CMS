from django.conf import settings
from django.db import models

from apps.academics.models import CourseOffering
from apps.common.models import TimeStampedModel


class LectureSession(TimeStampedModel):
    """A single lecture that actually took place for a course offering."""

    course_offering = models.ForeignKey(
        CourseOffering, on_delete=models.CASCADE, related_name='sessions'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topic_covered = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f'{self.course_offering} - {self.date}'


class AttendanceRecord(TimeStampedModel):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LEAVE = 'leave', 'Leave'
        LATE = 'late', 'Late'

    session = models.ForeignKey(LectureSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='attendance_records'
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['session']
        unique_together = ('session', 'student')

    def __str__(self):
        return f'{self.student.roll_number} - {self.session} - {self.get_status_display()}'
