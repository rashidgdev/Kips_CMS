from django.db import models

from apps.common.models import TimeStampedModel

from .offering import CourseOffering


class Enrollment(TimeStampedModel):
    class Status(models.TextChoices):
        ENROLLED = 'enrolled', 'Enrolled'
        DROPPED = 'dropped', 'Dropped'
        COMPLETED = 'completed', 'Completed'

    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='enrollments'
    )
    course_offering = models.ForeignKey(
        CourseOffering, on_delete=models.CASCADE, related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ENROLLED)

    class Meta:
        ordering = ['-enrolled_at']
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f'{self.student.roll_number} -> {self.course_offering}'
