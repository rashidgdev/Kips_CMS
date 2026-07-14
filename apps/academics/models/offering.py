from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel

from .course import Course
from .semester import Semester


class CourseOffering(TimeStampedModel):
    """A course assigned to a faculty member for a specific semester/section.

    This is the anchor row every later module (attendance, day book,
    assessments, timetable) hangs off of.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='offerings')
    teacher = models.ForeignKey(
        'accounts.TeacherProfile', on_delete=models.PROTECT, related_name='course_offerings'
    )
    section = models.CharField(max_length=10, default='A')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='course_offerings_assigned',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    max_seats = models.PositiveSmallIntegerField(default=60)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['semester', 'course', 'section']
        unique_together = ('course', 'semester', 'section')

    def __str__(self):
        return f'{self.course.code} ({self.semester}) - Section {self.section}'
