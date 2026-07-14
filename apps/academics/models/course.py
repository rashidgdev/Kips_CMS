from django.db import models

from apps.common.models import TimeStampedModel

from .program import Program


class Course(TimeStampedModel):
    class CourseType(models.TextChoices):
        THEORY = 'theory', 'Theory'
        LAB = 'lab', 'Lab'

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    credit_hours = models.PositiveSmallIntegerField(default=3)
    semester_number = models.PositiveSmallIntegerField(
        help_text='Position of this course in the program curriculum (1-based).'
    )
    course_type = models.CharField(
        max_length=20, choices=CourseType.choices, default=CourseType.THEORY
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['program', 'semester_number', 'code']

    def __str__(self):
        return f'{self.code} - {self.title}'
